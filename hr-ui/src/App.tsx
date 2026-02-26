import React, { useState } from "react";
import axios from "axios";
import {
  Layout,
  Typography,
  Upload,
  Button,
  Input,
  Avatar,
  List,
  Space,
  message,
  Divider,
} from "antd";
import {
  UploadOutlined,
  UserOutlined,
  RobotOutlined,
} from "@ant-design/icons";
import "./App.css";

const { Header, Content } = Layout;
const { Title, Text } = Typography;
const { TextArea } = Input;

type Role = "user" | "assistant";

interface ChatMessage {
  id: number;
  role: Role;
  text: string;
}

const App: React.FC = () => {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);

  const askQuestion = async () => {
    const trimmed = question.trim();
    if (!trimmed) return;

    const userMessage: ChatMessage = {
      id: Date.now(),
      role: "user",
      text: trimmed,
    };
    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");

    try {
      setLoading(true);
      const res = await axios.post(
        "http://127.0.0.1:8000/ask",
        null,
        { params: { question: trimmed } }
      );

      const botMessage: ChatMessage = {
        id: Date.now() + 1,
        role: "assistant",
        text: res.data.answer ?? "No answer returned.",
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      message.error("Failed to get answer from HR assistant.");
    } finally {
      setLoading(false);
    }
  };

  const uploadProps = {
    name: "file",
    accept: ".pdf,.txt",
    maxCount: 1,
    showUploadList: false,
    // Cast to any to satisfy Ant Design's customRequest signature while keeping our logic simple.
    customRequest: (async (options: any) => {
      const { file, onSuccess, onError } = options;
      const formData = new FormData();
      formData.append("file", file as File);

      try {
        await axios.post("http://127.0.0.1:8000/upload", formData);
        message.success("File uploaded successfully.");
        onSuccess?.();
      } catch (error) {
        message.error("File upload failed.");
        onError?.(error instanceof Error ? error : new Error(String(error)));
      }
    }) as any,
  };

  const handleKeyDown: React.KeyboardEventHandler<HTMLTextAreaElement> = (
    e
  ) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      askQuestion();
    }
  };

  return (
    <Layout className="app-layout">
      {/* <Header className="app-header">
        <div className="app-header-inner">
          <Title level={3} className="app-title">
            Smart HR Assistant
          </Title>
        </div>
      </Header> */}
      <Content className="app-content">
        <div className="chat-shell">
          <div className="top-row">
            <div className="top-row-left">
              <Text type="secondary">HR Knowledge Chat</Text>
            </div>
            <div className="top-row-right">
              <Upload {...uploadProps}>
                <Button type="default" icon={<UploadOutlined />}>
                  Upload Policy
                </Button>
              </Upload>
            </div>
          </div>

          <Divider className="chat-divider" />

          <div className="chat-container">
            <div className="chat-messages">
              {messages.length === 0 ? (
                <div className="chat-empty">
                  <Title level={4}>Welcome to your HR Assistant</Title>
                  <Text type="secondary">
                    Ask questions about HR policies, leave, benefits and more.
                  </Text>
                </div>
              ) : (
                <List
                  dataSource={messages}
                  renderItem={(msg: ChatMessage) => (
                    <List.Item
                      key={msg.id}
                      className={`chat-message chat-message-${msg.role}`}
                    >
                      <Space
                        align="end"
                        className="chat-message-inner"
                        size="small"
                      >
                        {msg.role === "assistant" && (
                          <Avatar
                            className="bot-avatar"
                            size="small"
                            icon={<RobotOutlined />}
                          />
                        )}
                        <div className="chat-bubble">
                          {msg.text.split("\n").map((line: string, idx: number) => (
                            <p key={idx}>{line}</p>
                          ))}
                        </div>
                      </Space>
                    </List.Item>
                  )}
                />
              )}
            </div>

            <div className="chat-input-row">
              <TextArea
                value={question}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setQuestion(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask HR a question..."
                autoSize={{ minRows: 1, maxRows: 3 }}
                className="chat-input"
              />
              <Button
                type="primary"
                icon={<UserOutlined />}
                onClick={askQuestion}
                loading={loading}
              >
                Send
              </Button>
            </div>
          </div>
        </div>
      </Content>
    </Layout>
  );
};

export default App;