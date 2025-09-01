import os
import json
import inspect
import datetime
from typing import Callable, Any, Dict, List

from dotenv import load_dotenv
import google.generativeai as genai

from .store_metadata import MetaData
from .retrieve_data import SqlData
from type_definitions import (
    FunctionResponse, 
    SchedulesResponse, 
    TimeResponse, 
    DatabaseInfoResponse,
    InterviewScheduleEntry
)

class GetFunctions:
    """Provides function tools for the Gemini chat model."""
    
    def __init__(self) -> None:
        """Initialize the function tools with database connections."""
        self._new_interview: MetaData = MetaData()
        self._get_data: SqlData = SqlData()

    def book_interview(self, name: str, email: str, date: str, time: str) -> FunctionResponse:
        """Book an interview with the provided details.
        
        Args:
            name: The name of the person being interviewed.
            email: The email address of the person.
            date: The date of the interview (e.g., "YYYY-MM-DD").
            time: The time of the interview (e.g., "HH:MM").
            
        Returns:
            A dictionary with status and message.
        """
        response: str = self._new_interview.add_interview(
            name=name, email=email, date=date, time=time
        )
        return FunctionResponse(
            status="success", 
            message=f"Interview for {name} has been booked for {date} at {time}."
        )

    def get_past_schedules(self) -> SchedulesResponse:
        """Retrieve and return a list of past interview schedules.
        
        Returns:
            A dictionary with status and list of schedules.
        """
        past_interviews = self._get_data.get_interview_data()

        serializable_interviews: List[InterviewScheduleEntry] = []
        for interview in past_interviews:
            interview_dict: Dict[str, Any] = {}
            
            for column in interview.__table__.columns:
                value = getattr(interview, column.name)
                if isinstance(value, datetime.datetime):
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
                elif isinstance(value, datetime.date):
                    value = value.strftime("%Y-%m-%d")
                elif isinstance(value, datetime.time):
                    value = value.strftime("%H:%M:%S")
                interview_dict[column.name] = value
            
            schedule_entry = InterviewScheduleEntry(
                id=interview_dict["id"],
                candidate_name=interview_dict["candidate_name"],
                candidate_email=interview_dict["candidate_email"],
                interview_date=interview_dict["interview_date"],
                interview_time=interview_dict["interview_time"]
            )
            serializable_interviews.append(schedule_entry)

        return SchedulesResponse(status="success", schedules=serializable_interviews)
    
    def get_current_time(self) -> TimeResponse:
        """Return the current date and time.
        
        Returns:
            A dictionary with the current time.
        """
        current_time: str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return TimeResponse(current_time=current_time)
    
    def retrieve_database_info(self, user_query: str) -> DatabaseInfoResponse:
        """Retrieve relevant information from the database to answer user questions.

        Args:
            user_query: The user's specific query string that needs to be answered 
                       using database information.
                       
        Returns:
            A dictionary with status and retrieved data.
        """
        response: str = self._get_data.all_context(query=user_query)
        return DatabaseInfoResponse(status="success", data=response)

    def get_function_declaration(self, func: Callable[..., Any]) -> Dict[str, Any]:
        """Create a function declaration for the Gemini API from a Python function.
        
        Args:
            func: The function to create a declaration for.
            
        Returns:
            A dictionary containing the function declaration.
        """
        signature = inspect.signature(func)
        params: Dict[str, Any] = {
            "type": "OBJECT",
            "properties": {},
            "required": [],
        }
        
        for name, param in signature.parameters.items():
            param_type: str = "STRING"
            description: str = f"The {name} for the interview."
            
            if func.__name__ == "retrieve_database_info" and name == "user_query":
                description = "The user's question or query that needs to be answered using database information."
            
            params["properties"][name] = {
                "type": param_type, 
                "description": description
            }
            if param.default is inspect.Parameter.empty:
                params["required"].append(name)
                
        return {
            "name": func.__name__,
            "description": func.__doc__.strip() if func.__doc__ else "",
            "parameters": params,
        }