from vivchain import BaseFunction
from .database import database
import json

def print_in_red(s):
     print(f'\x1b[0;37;41m||{s}||\x1b[0m')

def print_in_blue(s):
     print(f'\x1b[0;37;44m||{s}||\x1b[0m')

def print_in_green(s):
     print(f'\x1b[0;37;42m||{s}||\x1b[0m')

class post_solution(BaseFunction):
     
    def __call__(self, context, solution):
            hex_id = context['hex']
            
            print_in_red('Post -- Solution for {}'.format(hex_id))
            print_in_red(solution)

            #if id not in database.problem_cache: 
            database.problem_cache[hex_id] = solution
            database.post_solution(context, solution)

            confirmation = {
                "posted": True,
            }

            return json.dumps(confirmation)
    
    @staticmethod
    def schema():
        return {
                    "name": "post_solution",
                    "description": "Call this to submit the solution to a math problem. Show all work.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "solution": {
                                "type": "string",
                                "description": "The step by step solution to the problem or proof. Include final answer if appropriate",
                            },
                        },
                        "required": ["solution"],
                    },
                }

class post_grade(BaseFunction):
     
    def __call__(self, context, grade, pass_fail, feedback):
            
            hex_id = context['hex']
            print_in_red('Post -- Grade for {}'.format(hex_id))
            print_in_red('{} {} {}\n{}'.format(hex_id, grade, pass_fail, feedback))

            confirmation = {
                "hex_id": hex_id,
                "grade" : grade,
                "pass_fail": pass_fail
            }

            database.post_grade(context, grade, pass_fail, feedback)

            return json.dumps(confirmation)
    
    @staticmethod
    def schema():
        return {
                    "name": "post_grade",
                    "description": "Call this to submit grades for a teacher's performance",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "grade": {
                                "type": "string",
                                "enum": ["A", "B", "C", "D", "F"],
                                "description": "Letter grade evaluation of how well the teacher did.",
                            },
                            "pass_fail" : {
                                 "type": "string",
                                 "enum": ["pass", "fail"],
                                 "description": "Pass/fail was the teacher successful?" 
                            },
                            "feedback" : {
                                 "type": "string",
                                 "description": "Explain to the teacher feedback about their performance" 
                            }
                        },
                        "required": ["grade", "pass_fail", "feedback"],
                    },
                }
