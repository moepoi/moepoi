from python_graphql_client import GraphqlClient
import pathlib
import re
import os

root = pathlib.Path(__file__).parent.resolve()
client = GraphqlClient(endpoint="https://graphql.anilist.co")


TOKEN = os.environ.get("ANILIST_TOKEN", "")


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
query($favPage: Int) {
  Viewer {
    favourites {
      anime(page: $favPage) {
        nodes {
          title {
            romaji
          }
          siteUrl
        }
        pageInfo {
          total
          currentPage
          lastPage
          perPage
          hasNextPage
        }
      }
      manga(page: $favPage) {
        nodes {
          title {
            romaji
          }
          siteUrl
        }
        pageInfo {
          total
          currentPage
          lastPage
          perPage
          hasNextPage
        }
      }
      characters(page: $favPage) {
        nodes {
          name {
            full
          }
          siteUrl
        }
        pageInfo {
          total
          currentPage
          lastPage
          perPage
          hasNextPage
        }
      }
    }
  }
}
"""

def fetch_favorites(oauth_token):
    results = []
    variables = {"favPage": 1}
    data = client.execute(
        query=make_query(),
        variables=variables,
        headers={"Authorization": "Bearer {}".format(oauth_token)},
    )
    for x in data['data']['Viewer']['favourites']['anime']['nodes']:
        results.append(
            {
                'title': x['title']['romaji'],
                'url': x['siteUrl']
            }
        )
    return results   

if __name__ == "__main__":
    readme = root / "README.md"
    data = fetch_favorites(TOKEN)
    res = "\n".join(
        [
            "* [{title}]({url})".format(**x)
            for x in data
        ]
    )
    readme_contents = readme.open().read()
    rewritten = replace_chunk(readme_contents, "favorites_anime", res)
    readme.open("w").write(rewritten)
