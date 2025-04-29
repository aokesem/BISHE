import streamlit as st
import time
from test import liaotian,get_conversations,get_conversations_history,delete_conversation
from test import shangchuan,create_dataset,get_all_datasets,delete_dataset

#参数设置
api_key = "app-iZYWDyMQOeT33GRapi481vBR"#工作流apikey
dataset_api_key = "dataset-4oHPYmHQAD6R28gJ6lQ1ZGat"
user_id = "abc-123"


st.title("💬 Dify 聊天助手")
st.markdown("<small>本网站基于 Dify 提供智能问答与会话管理功能</small>", unsafe_allow_html=True)
st.sidebar.title("🔍 失效分析助手")

#初始化会话状态
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = ""
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation" not in st.session_state:
    st.session_state.conversations = []
#获取对话列表
conversations = get_conversations(api_key, user_id)
st.session_state.conversations = conversations

with st.expander("📌 当前对话信息", expanded=True):
    if st.session_state.conversation_id and st.session_state.conversations:
        conv_name = next(
            (conv["name"] for conv in st.session_state.conversations if conv["id"] == st.session_state.conversation_id),
            "未知对话名称"
        )
        st.markdown(f"**对话 ID**：`{st.session_state.conversation_id}`")
        st.markdown(f"**对话名称**：{conv_name}")
    else:
        st.markdown("暂无选中的对话。")

if st.sidebar.button("🆕 新建对话"):
    st.session_state.messages = []
    st.session_state.conversation_id = ""
    st.rerun()

if conversations:
    st.sidebar.header("对话列表")
    for i, conv in enumerate(conversations):
        conv_label = f"对话{i + 1}: {conv['name']}"
        if st.sidebar.button(conv_label, key=conv['id']):
            if conv['id'] != st.session_state.conversation_id:
                st.session_state.messages = get_conversations_history(api_key,conv['id'],user_id)
                st.session_state.conversation_id = conv['id']
                st.rerun()
    st.markdown("---")
    st.sidebar.markdown("### ⚠ 删除对话")

    # 是否确认删除框，仅在选中会话时显示
    confirm = False
    if st.session_state.get("conversation_id"):
        confirm = st.sidebar.checkbox("确认删除当前选中对话？")

    # 删除按钮始终显示，未选中会话时禁用
    delete_disabled = not st.session_state.get("conversation_id") or not confirm
    if st.sidebar.button("🗑 确认删除当前对话", disabled=delete_disabled):
        status, msg = delete_conversation(api_key, st.session_state.conversation_id, user_id)
        if status == 200:
            st.success("您已成功删除对话")
            time.sleep(2)
            st.session_state.conversation_id = None
            st.session_state.messages = []
            st.session_state.conversations = get_conversations(api_key, user_id)
            st.rerun()
        else:
            st.error(f"删除失败：{msg}")


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("请在这里输入问题")
if prompt:
    user_message = st.chat_message("human")
    user_message.write(prompt)
    st.session_state.messages.append({"role":"human","content":prompt})

    ai_message = st.chat_message("ai")
    ai_reply = liaotian(prompt,st.session_state.conversation_id)
    ai_message.write(ai_reply)
    st.session_state.messages.append({"role":"ai","content":ai_reply})
with st.sidebar:
    st.markdown("---")
    st.sidebar.markdown("### ⚠ 清空对话记录")
    if st.button("🧹 点击按钮清空对话记录"):
        st.session_state.messages = []
        st.session_state.conversation_id = ""
        st.rerun()
    st.markdown("---")
    # 初始化状态
    if "show_datasets" not in st.session_state:
        st.session_state.show_datasets = False
    # 切换显示状态
    if st.button("📚 查看知识库列表"):
        st.session_state.show_datasets = not st.session_state.show_datasets
    # 如果处于显示状态，就请求并展示数据集
    if st.session_state.show_datasets:
        datasets = get_all_datasets(dataset_api_key)  # 你之前定义好的获取数据集列表的函数
        if datasets:
            for ds in datasets:
                st.markdown(f"- **{ds['name']}**（ID: `{ds['id']}`）")
        else:
            st.info("暂无知识库数据")
    st.markdown("---")
    if "show_create_input" not in st.session_state:
        st.session_state.show_create_input = False
    if st.button("创建新知识库"):
        st.session_state.show_create_input = not st.session_state.show_create_input
    # 创建输入区域
    if st.session_state.show_create_input:
        dataset_name = st.text_input("知识库名称", key="create_dataset_name")
        if st.button("✅ 确认创建"):
            if dataset_name.strip():
                result = create_dataset(dataset_api_key, dataset_name)
                if result:
                    st.success(f"✅ 创建成功：{result['name']} (ID: {result['id']})")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("❌ 创建失败，请检查日志或接口返回")
            else:
                st.warning("请输入知识库名称")
    st.markdown("---")
    st.markdown("### 📤 上传文件")
    dataset_id = st.text_input("请输入目标知识库 ID", key="upload_dataset_id")
    uploaded_file = st.file_uploader("选择文件上传到 Dify 知识库")
    if uploaded_file is not None:
        if dataset_id.strip():
            shangchuan(uploaded_file, dataset_id.strip(), "abc-123")
        else:
            st.warning("⚠️ 请先输入目标知识库 ID")
    st.markdown("---")
    st.markdown("### 🗑 删除知识库")
    delete_dataset_id = st.text_input("请输入要删除的知识库 ID", key="delete_dataset_id")
    if st.button("❌ 删除该知识库"):
        if delete_dataset_id.strip():
            success = delete_dataset(dataset_api_key, delete_dataset_id.strip())
            if success:
                st.success(f"✅ 成功删除知识库：{delete_dataset_id.strip()}")
                time.sleep(2)
                st.rerun()
            else:
                st.error("❌ 删除失败，请检查 ID 是否正确或查看日志")
        else:
            st.warning("⚠️ 请输入要删除的知识库 ID")
    st.markdown("---")






