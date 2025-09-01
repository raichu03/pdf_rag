import os
import json
import inspect
import datetime
from typing import Callable, Any

from dotenv import load_dotenv
import google.generativeai as genai

from utils import MetaData
from .retrieve_data import SqlData


class GetFunctions:
    def __init__(self):
        self._new_interview = MetaData()
        self._get_data = SqlData()

    def book_interview(self, name: str, email: str, date: str, time: str):
        """
        Books an interview with the provided details.
        
        Args:
            name: The name of the person being interviewed.
            email: The email address of the person.
            date: The date of the interview (e.g., "YYYY-MM-DD").
            time: The time of the interview (e.g., "HH:MM").
        """
        
        response = self._new_interview.add_interview(name=name, email=email, date=date, time=time)
        return {"status": "success", "message": f"Interview for {name} has been booked for {date} at {time}."}

    def get_past_schedules(self):
        """
        Retrieves and returns a list of past interview schedules.
        """
        past_interviews = self._get_data.get_interview_data()

        serializable_interviews = []
        serializable_interviews = []
        for interview in past_interviews:
            interview_dict = {}
            
            for column in interview.__table__.columns:
                value = getattr(interview, column.name)
                if isinstance(value, datetime.datetime):
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
                elif isinstance(value, datetime.date):
                    value = value.strftime("%Y-%m-%d")
                elif isinstance(value, datetime.time):
                    value = value.strftime("%H:%M:%S")
                interview_dict[column.name] = value
            
            serializable_interviews.append(interview_dict)
        
        print("--- Function Called: get_past_schedules ---")
        print("Retrieving past interview schedules...")
        print("--- End Function Call ---")
        return {"status": "success", "schedules": serializable_interviews}
    
    def get_current_time(self):
        """
        Returns the current date and time.
        """
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("--- Function Called: get_current_time ---")
        print(f"Current time is: {current_time}")
        print("--- End Function Call ---")
        return {"current_time": current_time}

    def get_function_declaration(self, func: Callable) -> dict:
        """Creates a function declaration for the Gemini API from a Python function."""
        signature = inspect.signature(func)
        params = {
            "type": "OBJECT",
            "properties": {},
            "required": [],
        }
        for name, param in signature.parameters.items():
            param_type = "STRING"
            params["properties"][name] = {
                "type": param_type, 
                "description": f"The {name} for the interview."
            }
            if param.default is inspect.Parameter.empty:
                params["required"].append(name)
                
        return {
            "name": func.__name__,
            "description": func.__doc__.strip(),
            "parameters": params,
        }