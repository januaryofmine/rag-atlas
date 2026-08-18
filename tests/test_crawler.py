from crawler.collect import discover_repositories


class FakeGitHub:
    def search_repositories(self, query: str, *, max_pages: int = 1):
        del max_pages
        if query == "q1":
            yield {"id": 1, "full_name": "a/rag"}
            yield {"id": 2, "full_name": "b/rag"}
        if query == "q2":
            yield {"id": 1, "full_name": "a/rag"}


def test_discovery_dedupes_but_keeps_query_provenance():
    repos = discover_repositories(FakeGitHub(), ["q1", "q2"], max_repos=10)
    assert [repo.github_id for repo in repos] == [1, 2]
    assert repos[0].queries == ["q1", "q2"]
