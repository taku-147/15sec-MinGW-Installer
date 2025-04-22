import sys
import stat
from ctypes import windll
import os
import re
import py7zr
import requests
import ctypes
import shutil

print("**********************************")
print("***** 15 Sec MinGW Installer *****")
print("***** by Taku(an)_147        *****")
print("**********************************")
print("\n")
print("15秒でMinGW環境を構築するPythonコードです。")

#もし、管理者権限を持っていない時
is_admin = ctypes.windll.shell32.IsUserAnAdmin()
if not is_admin:
    print("管理者権限で実行してください。")

    #UAEを表示して自分自身を再実行
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    exit()

#ダウンロードセクション
def download_link_get():
    #mingw-builds-binariesのURL
    url = "https://github.com/niXman/mingw-builds-binaries/releases/latest"
    print("バージョンをチェック中...")
    #URLにアクセスして最新のリリースページを取得
    response = requests.get(url, allow_redirects=True)
    #サーバーからエラーが帰ってきたとき
    if response.status_code != 200:
        print("エラー:URLにアクセスできません。")
        end()

    #リダイレクトされたURLを取得
    latest_release_url = response.url
    release_page = requests.get(latest_release_url).text

    # バージョン情報を取得する正規表現(例: 14.2.0-rt_v12-rev2)
    version_pattern = r"\d+\.\d+\.\d+-rt_v\d+-rev\d+"

    # 正規表現を使用してバージョン情報を抽出
    version_match = re.search(version_pattern, release_page)

    # バージョン情報が見つかった場合
    if version_match:
        print(f"MinGW {version_match.group(0)}")
        v_pattern  = version_match.group(0).split("-rt_v")
        # Windows用のMinGWをダウンロードするためのURLを生成
        file_name = f"x86_64-{v_pattern[0]}-release-win32-seh-msvcrt-rt_v{v_pattern[1]}.7z"
        download_url = f"https://github.com/niXman/mingw-builds-binaries/releases/latest/download/{file_name}"
        return file_name ,download_url

    # バージョン情報が見つからなかった場合
    else:
        print("エラー:ダウンロードリンクが見つかりません。")
        end()

def file_downloader(url):
    # 一時ディレクトリに移動
    temp_dir = os.path.join(os.getenv("LOCALAPPDATA"), "Temp")
    file_name = url.split("/")[-1]
    save_path = os.path.join(temp_dir, file_name)
    # 一時ディレクトリ先に最新版のMinGWデータがある場合はダウンロードをスキップ
    if(os.path.exists(save_path)):
        os.remove(save_path)
    print(f"ダウンロード中です。時間がかかることがあります。")

    # URLからファイルをダウンロード
    response = requests.get(url, stream=True)
    # サーバーからエラーが帰ってきたとき
    if response.status_code != 200:
        print("エラー:ファイルのダウンロードに失敗しました。")
        exit(1)

    # ダウンロードしたファイルを保存
    with open(save_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    print(f"ダウンロード完了しました。")

def unarchiver(file_name):
    # 一時ディレクトリに移動
    temp_dir = os.path.join(os.getenv("LOCALAPPDATA"), "Temp")
    file_path = os.path.join(temp_dir, file_name)
    # 7zファイルの解凍先を指定
    extract_path = os.path.join("C:\\", "mingw")  # 解凍先ディレクトリ

    # 既存のMinGWがある場合は削除
    if os.path.exists(extract_path):
        print(f"既存のディレクトリを削除しています: {extract_path}...")
        shutil.rmtree(extract_path, onexc=on_rm_error)  # ディレクトリ削除

    # 解凍先ディレクトリが存在しない場合は作成
    if not os.path.exists(extract_path):
        os.makedirs(extract_path)

    # 7zファイルを解凍
    print(f"ファイルを解凍中...")
    with py7zr.SevenZipFile(file_path, mode='r') as archive:
        archive.extractall(path=extract_path)
    print(f"ファイル解凍完了")

    # Tempファイルを削除
    os.remove(file_path)
    print(f"Tempファイルを削除しました")


# 環境変数にPathを追加
def environment_setting():
    mingw_bin_path = "C:\\mingw\\mingw64\\bin"
    current_path = os.environ.get("Path", "")

    if mingw_bin_path not in current_path:
        print("システム環境変数にPathを追加しています...")
        windll.kernel32.SetEnvironmentVariableW("Path", f"{current_path};{mingw_bin_path}")
        print(f"Pathに追加しました: {mingw_bin_path}")
    else:
        print("Pathに既に追加されています。")

# ディレクトリ削除時のエラー処理
def on_rm_error(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)

# 終了処理
def end():
    print("Enterキーを押して終了します。")
    input()
    exit(0)

print("Enterキーを押すとインストールを開始します。")
input()
file_name, link = download_link_get()

file_downloader(link)

unarchiver(file_name)

environment_setting()

print("MinGWのインストールが完了しました。")
end()
