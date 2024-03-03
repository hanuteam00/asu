from database import Database
import json

if __name__ == '__main__':
    with Database() as db:
        if db:
            contents = db.execute_from_file('content')
            for row in contents:
                if row['content_type'] == 'try_it':
                    print(row['content'])
                    #break
               