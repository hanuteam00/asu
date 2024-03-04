import json
from asu.database import database
from repair_args.repair import repair_args
from openai import OpenAI
import httpx
import time

def print_in_red(s):
     print(f'\x1b[0;37;41m||{s}||\x1b[0m')

def pretty_print(messages):
    print("# Messages")
    for m in messages:
        print(f"{m.role}: {m.content[0].text.value}")
    print()

class Agent:

    def __init__(self, system_prompt, functions, model='gpt-4-1106-preview', verbose=False, thread_id=None, use_CI=True):
        self.verbose = verbose
        self.chat_history = []

        self.client = OpenAI()

        self.model = model

        self.context = None

        self.functions = {}
        self.function_schemas = []
        for f in functions:
            self.functions[f.__name__] = f
            self.function_schemas.append(f.schema())
        
        if use_CI:
            tools = [{"type": "code_interpreter"}]
        else:
            tools = []

        for f in functions:
            tools.append({"type": "function", "function": f.schema()})

        self.assistant = self.client.beta.assistants.create(
            name="Math Tutor",
            instructions=system_prompt,
            tools=tools,
            model=model
        )

        if thread_id:
            self.thread = self.client.beta.threads.retrieve(thread_id=thread_id)
        else:
            self.thread = self.client.beta.threads.create()

        self.seen_message_ids = set()
        


    def set_context(self, context):
        self.context = context

    def human_send(self, user_message):
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id, role="user", content=user_message
        )

    def submit(self, payload):
        old_status = ''

        self.human_send(payload)
        self.run = self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                
            )
        

        while True:

            self.run = self.client.beta.threads.runs.retrieve(
                run_id=self.run.id,
                thread_id=self.thread.id
                )
            
            if self.run.status != old_status:
                #print(self.run.status)
                old_status = self.run.status
            
            if self.run.status == 'requires_action':
                
                tool_calls = self.run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []

                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    arguments = tool_call.function.arguments

                    default_arg_lookup = {
                        'execute_python': 'code',
                        'send_message_to_besh': 'message',
                        'post_solution': 'solution'
                    }


                    ## clean up arguments if needed
                    original_arg = arguments

                    default_arg = None
                    if function_name in default_arg_lookup:
                        default_arg = default_arg_lookup[function_name]
                    repaired_args = repair_args(arguments, default_arg=default_arg)

                    try:
                        kwargs = json.loads(repaired_args, strict=False)
                    except json.decoder.JSONDecodeError as e:

                        print('JSON ERROR DURING FUNCTION CALL')
                        
                        print(function_name)
                        print(e)
                        print(original_arg)
                        print('===')
                        print(repaired_args)

                        key = '|' + e.msg + '|\n|' + repr(original_arg) + '|\n|' + repr(repaired_args) + '|'
                        database.log_json_error(key)
                        function_message = {
                            "name": function_name,
                            "content": 'JSON_DECODE_ERROR',
                        }
                        tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": json.dumps(function_message),
                        })
                        continue
                    

                    if self.context:
                        kwargs['context'] = self.context

                    f = self.functions[function_name]()
                    function_response = f(**kwargs)
                    tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": json.dumps(function_response),
                        })


                self.run = self.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=self.thread.id,
                    run_id=self.run.id,
                    tool_outputs=tool_outputs,
                )

            if self.run.status in ['completed', 'failed', 'cancelled', 'expired']:
                if self.run.status != 'completed':
                    print(self.run.status)
                break
            #print(self.run.status)
            time.sleep(0.5)

        messages = self.client.beta.threads.messages.list(self.thread.id).data


        #print(messages)
        if messages:
            response = ''
            for message in reversed(messages):
                if message.role != 'assistant':
                    continue
                message_id = message.id
                if message_id in self.seen_message_ids:
                    continue
                self.seen_message_ids.add(message_id)
                if message.content[0].type == 'text' and message.content[0].text.value:
                    if response:
                        response += '\n'
                    response += message.content[0].text.value

            return response
        else:
            return ''

    def clear(self):
        self.context = None
        self.thread = self.client.beta.threads.create()

