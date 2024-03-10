import redis  # library for working with Redis
from uuid import uuid4 as uuid  # generating UUIDs
import json  # work with json
import zulu  # handling time in UTC in DB


class Database:

    def __init__(self):  # constructor for the Database class, same as this.
        # initialize a connection to the Redis database using the provided parameters
        print("Connecting to database...")
        self.r = redis.Redis(
            host="us1-close-pigeon-41232.upstash.io",
            port="41232",
            username="default",
            password="13e9b502ee444850bf30f89f6016fa5c",
            ssl=True,
            # retrieved values are decoded from bytes to strings
            decode_responses=True,
        )
        #initialize self.problem_cache as an empty dictionary, which could be used to cache problems if needed
        self.problem_cache = {}

    # Does not check for duplicates!
    def add_prompt(self, namespace, prompt, problem, solution):
        rand_uuid = str(uuid().hex)
        problem = {
            "hex": rand_uuid,
            "problem": problem,
            "solution": solution,
            "teacher_prompt": prompt,
        }
        json_string = json.dumps(problem)
        self.r.sadd("{}:prompts".format(namespace), json_string)

    def get_prompts(self, namespace):

        iterable = self.r.sscan_iter("{}:prompts".format(namespace))

        for json_string in iterable:
            record = json.loads(json_string)
            yield record

    def post_grade(self, context, grade, solved, feedback):
        namespace = context["namespace"]
        hex_id = context["hex"]
        # context['execution']['grade_finished_at'] = str(zulu.now())

        record = {
            "hex_id": hex_id,
            "grade": grade,
            "pass_fail": solved,
            "feedback": feedback,
            "chat_log": context["chat_log"],
            "teacher_prompt": context["teacher_prompt"],
            "student_prompt": context["student_prompt"],
            "grader_prompt": context["grader_prompt"],
        }
        grade_string = json.dumps(record)
        self.r.hset("{}:grades".format(namespace["name"]), hex_id, grade_string)

    def grade_exists(self, context):
        namespace = context["namespace"]
        hex_id = context["hex"]

        grades_key = "{}:grades".format(namespace["name"])
        return self.r.hexists(grades_key, hex_id)

    def add_task(self, verb, context, priority=1):
        key = "{}:job_queue".format(context["namespace"]["name"])

        # Temporary solution, OpenAI objects not serializable
        if "besh_context" in context:
            del context["besh_context"]

        # print(context)

        job = {"verb": verb, "context": context}
        json_string = json.dumps(job)
        self.r.zadd(key, {json_string: priority}, incr=True)

    def log_json_error(self, key):
        self.r.lpush("json_error", key)

    def log_function_key_error(self, key):
        self.r.lpush("function_key_error", key)

    def get_tasks(self, context):
        key = "{}:job_queue".format(context["namespace"]["name"])
        pop = self.r.zpopmax(key)
        while pop:
            yield json.loads(pop[0][0])
            pop = self.r.zpopmax(key)

    def delete_namespace_by_ref(self, namespace_ref):
        print("Deleting " + namespace_ref)
        iterable = self.r.scan_iter("{}:*".format(namespace_ref))
        for key in iterable:
            print(key)
            self.r.delete(key)

    def get_grades(self, context):
        namespace = context["namespace"]
        grades = self.r.hscan_iter("{}:grades".format(namespace["name"]))

        for key, value in grades:
            record = json.loads(value)
            record.update({"hex_id": key})
            yield record


database = Database()
