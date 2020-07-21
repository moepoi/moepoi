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

def fetch_favorites(oauth_token, types='anime'):
    results = []
    variables = {"favPage": 1}
    data = client.execute(
        query=make_query(),
        variables=variables,
        headers={"Authorization": "Bearer {}".format(oauth_token)},
    )
    for x in data['data']['Viewer']['favourites'][types]['nodes']:
        results.append(
            {
                'title': x['title']['romaji'] if types != 'characters' else x['name']['full'],
                'url': x['siteUrl']
            }
        )
    return results   

if __name__ == "__main__":
    readme = root / "README.md"
    readme_contents = readme.open().read()
    # Favorites Anime
    data = fetch_favorites(TOKEN, types='anime')
    res = "\n".join(
        [
            "* [{title}]({url})".format(**x)
            for x in data
        ]
    )
    rewritten = replace_chunk(readme_contents, "favorites_anime", res)
    # Favorites Manga
    data = fetch_favorites(TOKEN, types='manga')
    res = "\n".join(
        [
            "* [{title}]({url})".format(**x)
            for x in data
        ]
    )
    rewritten = replace_chunk(readme_contents, "favorites_manga", res)
    # Favorites Characters
    data = fetch_favorites(TOKEN, types='characters')
    res = "\n".join(
        [
            "* [{title}]({url})".format(**x)
            for x in data
        ]
    )
    rewritten = replace_chunk(readme_contents, "favorites_characters", res)
    
    readme.open("w").write(rewritten)
