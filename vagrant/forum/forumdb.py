#
# Database access functions for the web forum.
#

import time
import psycopg2
import bleach

## Database connection



## Get posts from database.
def GetAllPosts():
    '''Get all the posts from the database, sorted with the newest first.

    Returns:
      A list of dictionaries, where each dictionary has a 'content' key
      pointing to the post content, and 'time' key pointing to the time
      it was posted.
    '''
    conn = psycopg2.connect("dbname=forum")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts ORDER BY time DESC")
    posts = ({'content': str(row[1]), 'time': str(row[0])}
             for row in cursor.fetchall())
    conn.close()
    return posts

## Add a post to the database.
def AddPost(content):
    '''Add a new post to the database.

    Args:
      content: The text content of the new post.
    '''
    content = bleach.clean(content)
    conn = psycopg2.connect("dbname=forum")
    cursor = conn.cursor()
    # use query parameters instead of string substitutions
    cursor.execute("INSERT INTO posts (content) VALUES (%s)", (content, ))
    conn.commit()
    conn.close()
