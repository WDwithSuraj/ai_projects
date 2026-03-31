from bs4 import BeautifulSoup
import requests

# Standard headers to fetch a website
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}


def fetch_website_contents(url):
    """
    Return the title and contents of the website at the given url;
    truncate to 2,000 characters as a sensible limit
    """
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.title.string if soup.title else "No title found"
    if soup.body:
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        text = soup.body.get_text(separator="\n", strip=True)
    else:
        text = ""
    return (title + "\n\n" + text)[:2_000]

def fetch_website_links(url):
    """
    Return the links on the webiste at the given url
    I realize this is inefficient as we're parsing twice! This is to keep the code in the lab simple.
    Feel free to use a class and optimize it!
    """
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    links = [link.get("href") for link in soup.find_all("a")]
    return [link for link in links if link]



# Class based - optimization over the above methods.
class WebsiteScraper:
    def __init__(self, url: str):
        self.url = url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        self._response = None
        self._soup = None

    def _fetch(self):
        """Fetch the website only once"""
        if self._response is None:
            self._response = requests.get(self.url, headers=self.headers, timeout=10)
            self._response.raise_for_status()

    def _parse(self):
        """Parse HTML only once"""
        if self._soup is None:
            self._fetch()
            self._soup = BeautifulSoup(self._response.content, "html.parser")

    def get_title_and_text(self, char_limit: int = 2000) -> str:
        self._parse()

        title = self._soup.title.string if self._soup.title else "No title found"

        if self._soup.body:
            for tag in self._soup.body(["script", "style", "img", "input"]):
                tag.decompose()

            text = self._soup.body.get_text(separator="\n", strip=True)
        else:
            text = ""

        return (title + "\n\n" + text)[:char_limit]

    def get_links(self) -> list[str]:
        self._parse()

        links = [a.get("href") for a in self._soup.find_all("a")]
        return [link for link in links if link]

    def get_all(self) -> dict:
        """Convenience method for pipeline usage"""
        return {
            "url": self.url,
            "content": self.get_title_and_text(),
            "links": self.get_links()
        }