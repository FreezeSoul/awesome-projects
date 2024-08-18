"""
每周定时更新 GitHub Star 仓库的项目描述到 README.md 文件中
"""
import os
from github import Github
from pathlib import Path
from googletrans import Translator
import requests
from tqdm import tqdm


REPO_PATH = Path(__file__).resolve().parent

translator = Translator()
GITHUB_TOKEN = os.getenv("GIT_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError("GIT_TOKEN is not set or is empty")

print(f"GIT_TOKEN: {GITHUB_TOKEN}")  # 调试信息

g = Github(GITHUB_TOKEN)

user = g.get_user()

starred_repos = user.get_starred()

def get_repo_description(repo):
    if repo.description:
        return repo.description
    repo_readme_url = f"https://api.github.com/repos/{repo.full_name}/readme"
    headers = {"Accept": "application/vnd.github.v3.raw"}
    response = requests.get(repo_readme_url, headers=headers, auth=(user.login, GITHUB_TOKEN))
    response.raise_for_status()
    for line in response.text.split("\n"):
        stripped_line = line.strip()
        if stripped_line.startswith('#'):
            return stripped_line.replace("#", "").strip()

# 准备 Markdown 内容
markdown_content = "# High-Quality Open Source Project Repositories\n\n# 高质量开源仓库\n\n### 整理感兴趣的高质量开源项目仓库，方便查阅。\n\n|项目名|项目描述|中文项目描述|\n|---|---|---|\n"
for repo in starred_repos:
    repo_name = repo.full_name.split("/")[-1]
    repo_url = repo.html_url
    
    repo_description = get_repo_description(repo)
    if repo_description and isinstance(repo_description, str):
        if len(repo_description) > 100:
            repo_description = repo_description[:100] + "..."
        repo_description_zh = translator.translate(repo_description, dest="zh-CN").text
    # 整理成 Markdown 表格格式|项目名|项目链接|项目描述|中文项目描述|
    markdown_content += f"|[{repo_name}]({repo_url})|{repo_description}|{repo_description_zh}|\n"

# 将 Markdown 内容写入 README.md 文件
readme_path = os.path.join(REPO_PATH, "README.md")
with open(readme_path, "w", encoding="utf-8") as file:
    file.write(markdown_content)

print(f"README.md file has been updated with starred repositories.")

