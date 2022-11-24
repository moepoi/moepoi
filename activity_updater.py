from python_graphql_client import GraphqlClient
import requests
import json
import pathlib
import re
import os

root = pathlib.Path(__file__).parent.resolve()
client = GraphqlClient(endpoint="https://graphql.anilist.co")


TOKEN = os.environ.get("ANILIST_TOKEN", "")
SHARE_TOKEN = os.environ.get("SHARE_TOKEN", "")

def replace_chunk(content, marker, chunk, inline=False):
    r = re.compile(
        r"<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->".format(marker, marker),
        re.DOTALL,
    )
    if not inline:
        chunk = "\n{}\n".format(chunk)
    chunk = "<!-- {} starts -->{}<!-- {} ends -->".format(marker, chunk, marker)
    return r.sub(chunk, content)

def make_query():
    return """
query ActivityQuery(
  $page: Int
  $perPage: Int
  $type_in: [ActivityType]
  $userId: Int
  $userId_in: [Int]
  $userId_not_in: [Int]
  $isFollowing: Boolean
) {
  Page(page: $page, perPage: $perPage) {
    pageInfo {
      total
      perPage
      currentPage
      lastPage
      hasNextPage
    }
    activities(
      type_in: $type_in
      userId: $userId
      userId_in: $userId_in
      userId_not_in: $userId_not_in
      isFollowing: $isFollowing
      sort: [ID_DESC]
    ) {
      __typename
      ...onTextActivity
      ...onListActivity
      ...onMessageActivity
    }
  }
}

fragment onTextActivity on TextActivity {
  id
  userId
  type
  replyCount
  text
  siteUrl
  isSubscribed
  likeCount
  isLiked
  createdAt
  user {
    id
    name
    avatar {
      medium
    }
  }
  replies {
    id
    userId
    activityId
    text
    likeCount
    isLiked
    createdAt
    user {
      id
      name
      avatar {
        medium
      }
    }
    likes {
      id
      name
      avatar {
        medium
      }
    }
  }
  likes {
    id
    name
    avatar {
      medium
    }
  }
}

fragment onListActivity on ListActivity {
  id
  userId
  type
  replyCount
  status
  progress
  isSubscribed
  likeCount
  isLiked
  siteUrl
  createdAt
  user {
    id
    name
    avatar {
      medium
    }
  }
  media {
    id
    title {
      userPreferred
    }
    type
    format
    startDate {
      year
      month
      day
    }
    coverImage {
      medium
    }
  }
  replies {
    id
    userId
    activityId
    text
    likeCount
    isLiked
    createdAt
    user {
      id
      name
      avatar {
        medium
      }
    }
    likes {
      id
      name
      avatar {
        medium
      }
    }
  }
  likes {
    id
    name
    avatar {
      medium
    }
  }
}

fragment onMessageActivity on MessageActivity {
  id
  recipientId
  messengerId
  type
  replyCount
  message
  isSubscribed
  likeCount
  isLiked
  isPrivate
  siteUrl
  createdAt
  recipient {
    id
    name
    avatar {
      medium
    }
  }
  messenger {
    id
    name
    avatar {
      medium
    }
  }
  replies {
    id
    userId
    activityId
    text
    likeCount
    isLiked
    createdAt
    user {
      id
      name
      avatar {
        medium
      }
    }
    likes {
      id
      name
      avatar {
        medium
      }
    }
  }
  likes {
    id
    name
    avatar {
      medium
    }
  }
}
"""

def fetch_activity(oauth_token, userId):
    results = []
    variables = {"page": 1, "perPage": 10, "userId": userId}
    data = client.execute(
        query=make_query(),
        variables=variables,
        headers={"Authorization": "Bearer {}".format(oauth_token)},
    )
    for x in data['data']['Page']['activities']:
        try:
            results.append(
                {
                    'status': x['status'].capitalize(),
                    'progress': x['progress'],
                    'activity_url': x['siteUrl'],
                    'title': x['media']['title']['userPreferred'],
                    'url': f"https://anilist.co/{x['media']['type'].lower()}/{str(x['media']['id'])}"
                }
            )
        except:
            pass
    return results

def share_activity(token, text, visibility):
    try:
        url = "https://moe.onl/api/notes/create"

        payload = json.dumps({
          "i": token,
          "text": text,
          "visibility": visibility
        })
        headers = {
          'Content-Type': 'application/json'
        }

        requests.request("POST", url, headers=headers, data=payload)
    except Exception as e:
        print (e)

if __name__ == "__main__":
    readme = root / "README.md"
    readme_contents = readme.open().read()
    # List Activity
    data = fetch_activity(TOKEN, userId=161753)
    if data[0]['progress'] != None:
        share_text = f"{data[0]['status']} {data[0]['progress']} of [{data[0]['title']}]({data[0]['url']})"
    else:
        share_text = f"{data[0]['status']} [{data[0]['title']}]({data[0]['url']})"
    share_activity(SHARE_TOKEN, share_text, "public")
    res = "\n".join(
        [
            "* [{status} {progress}]({activity_url}) of [{title}]({url})".format(**x)
            for x in data
        ]
    )
    print (res)
    rewritten = replace_chunk(readme_contents, "anilist_activity", res)
    
    readme.open("w").write(rewritten)
