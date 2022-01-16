import json
from multiprocessing.pool import ThreadPool

import httpx
import yaml

SESSION = httpx.Client()
GH_INFO = {
    "desc": "description",
    "forks": None,
    "issues": "open_issues_count",
    "stars": "stargazers_count",
    "tags": "topics",
    "watching": "subscribers_count",
}

import click

@click.command()
@click.argument('kv')
def main(kv):
    op = []

    with open("repos.yml", "r") as f:
        RYML = yaml.safe_load(f)

    def info(item):
        k, v = item
        repo = f'https://github.com/{v["user"]}/{k}'
        rl = v["links"]
        rl = rl if rl else {}
        links = {"repo": repo, **rl}
        resp = SESSION.get(f'https://api.github.com/repos/{v["user"]}/{k}').json()

        info = {}

        for ghk, ghv in GH_INFO.items():
            info[ghk] = resp[ghv if ghv else ghk]
        if rl:
            dll = rl.get("dl")
            if dll:
                links["dl"] = dll
        else:
            if v["release"]:
                links["dl"] = f'{repo}/releases'

        op.append({
            "name": k,
            "links": links,
            **info
        })

    with ThreadPool(20) as pool:
        pool.map(info, RYML["repos"].items())
        pool.close()
        pool.join()

    SESSION.post(f'https://{kv}.whi-ne.workers.dev', json={"pirate_kings": json.dumps(op, indent=None)})

if __name__ == '__main__':
    main()