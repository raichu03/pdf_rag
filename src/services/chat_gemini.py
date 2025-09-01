import os
from typing import List, Dict

from dotenv import load_dotenv
import google.generativeai as genai

from utils import GetFunctions

class ChatRag:
    def __init__(self):
        self._all_tools = GetFunctions()
        load_dotenv()

        self._gemini_key = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=self._gemini_key)

        self._tools = genai.protos.Tool(
            function_declarations=[
                self._all_tools.get_function_declaration(self._all_tools.book_interview),
                self._all_tools.get_function_declaration(self._all_tools.get_past_schedules),
                self._all_tools.get_function_declaration(self._all_tools.get_current_time),
            ]
        )

        self._model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            tools=[self._tools]
        )

        self._function_map = {
            "book_interview": self._all_tools.book_interview,
            "get_past_schedules": self._all_tools.get_past_schedules,
            "get_current_time": self._all_tools.get_current_time,
        }

    def conversation(self, user_input: str, chat_history: List[Dict]):
        chat = self._model.start_chat(history=chat_history)

            
        response = chat.send_message(user_input)

        if response.candidates and response.candidates[0].content:
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    function_name = part.function_call.name
                    arguments = {k: v for k, v in part.function_call.args.items()} # Ensure arguments are a standard dict

                    if function_name in self._function_map:
                        try:
                            result = self._function_map[function_name](**arguments)
                            
                            tool_response = chat.send_message([
                                genai.protos.Part(
                                    function_response=genai.protos.FunctionResponse(
                                        name=function_name,
                                        response={"result": result}
                                    )
                                )
                            ])
                            return f"{tool_response.text}"
                        except TypeError as e:
                            print(f"Error calling function '{function_name}': {e}")
                            return "Assistant: I couldn't process your request due to missing information. Can you please provide all the details?"
                    else:
                        return f"Assistant: I'm sorry, I don't have a tool to perform the action '{function_name}'."
                elif part.text:
                    return f"Assistant: {part.text}"
        else:
            return "Assistant: I couldn't generate a response. Please try again."