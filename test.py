import requests
import json
import streamlit as st



def liaotian(query,conversation_id):
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = ""
    url = 'http://localhost/v1/chat-messages'
    api_key = "app-iZYWDyMQOeT33GRapi481vBR"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    data = {
        "inputs": {},
        "query": query,
        "response_mode": "blocking",
        "conversation_id": conversation_id,
        "user": "abc-123"
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    result = response.json()
    st.session_state.conversation_id = result.get("conversation_id")
    return result.get("answer")


def get_conversations(api_key,user_id,base_url='http://localhost/v1'):
    url = f"{base_url}/conversations"
    headers = {
        'Authorization':f'Bearer {api_key}'
    }
    params ={
        'user':user_id,
        'limit':30
    }
    response = requests.get(url,headers=headers,params=params)
    conversations = response.json().get('data', [])
    return [{"id": conv["id"], "name": conv["name"]} for conv in conversations]
    #[{'id': 'a43048fb-d595-4ac9-9837-5f70a9c60f6f', 'name': '向我问候☺️'}]
def get_conversations_history(api_key,conversation_id,user_id,base_url='http://localhost/v1'):
    url = f"{base_url}/messages"
    headers = {
        'Authorization':f'Bearer {api_key}',
    }
    params = {
        'conversation_id': conversation_id,
        'user':user_id,
        'first_id': None,
        'limit':30
    }
    response = requests.get(url, headers=headers, params=params)
    messages_raw = response.json().get("data",[])
    messages_raw.reverse()
    messages = []
    for msg in messages_raw:
        if msg.get("query"):
            messages.append({"role": "user", "content": msg["query"]})
        if msg.get("answer"):
            messages.append({"role":"ai","content":msg["answer"]})
    return messages
# api_key = "app-iZYWDyMQOeT33GRapi481vBR"
# user_id = "abc-123"
# conversation_id = "5554aacc-caad-48ea-bd10-bded0af49f31"
# a = get_conversations_history(api_key,conversation_id,user_id)
# print(a)

def delete_conversation(api_key,conversation_id,user_id,base_url='http://localhost/v1'):
    url = f"{base_url}/conversations/{conversation_id}"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        'user': user_id
    }
    try:
        response = requests.delete(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get("result") == "success":
                return 200, "对话删除成功"
            else:
                return 400, "删除失败，未知错误"
        else:
            return response.status_code, response.text
    except requests.exceptions.RequestException as e:
        return 500, str(e)

############## 知识库修改  #####################
def shangchuan(file, dataset_id, user="abc-123"):
    url = f"http://localhost/v1/datasets/{dataset_id}/document/create-by-file"
    api_key = "dataset-4oHPYmHQAD6R28gJ6lQ1ZGat"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    process_rule = {
        "mode": "automatic",
        "rules": {
            "pre_processing_rules": [
                {"id": "remove_extra_spaces", "enabled": True},
                {"id": "remove_urls_emails", "enabled": True}
            ],
            "segmentation": {
                "separator": "\n",
                "max_tokens": 1000
            }
        }
    }
    files = {
        'file': (file.name, file, file.type),
    }
    data = {
        "indexing_technique": "high_quality",
        "process_rule": process_rule
    }
    mydata = {
        'data': json.dumps(data)
    }
    try:
        response = requests.post(url, headers=headers, files=files, data=mydata)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"HTTP错误发生: {err}")
        print(f"响应内容: {err.response.text}")
        return None
def create_dataset(api_key,dataset_name,base_url="http://localhost/v1"):
    url = f"{base_url}/datasets"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        "name": dataset_name,
        "indexing_technique":'high_quality'
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"创建失败：{response.json().get('message', '未知错误')}")
        return None
import requests

def get_all_datasets(api_key, base_url="http://localhost/v1", page=1, limit=20):
    url = f"{base_url}/datasets?page={page}&limit={limit}"
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        st.error(f"获取知识库失败：{response.json().get('message', '未知错误')}")
        return []
def delete_dataset(api_key,dataset_id,base_url="http://localhost/v1"):
    url = f"{base_url}/datasets/{dataset_id}"
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        return True
    else:
        st.error(f"删除失败：{response.status_code} - {response.text}")
        return False
