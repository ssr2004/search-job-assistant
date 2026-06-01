import { useState } from 'react'
import { Input, Button, List, Typography, Space } from 'antd'
import { SendOutlined } from '@ant-design/icons'

const { Text } = Typography

interface Message {
  role: 'user' | 'assistant'
  content: string
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSend = () => {
    if (!input.trim()) return

    const userMessage: Message = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    // 模拟响应 - TODO: 接入 SSE 流式响应
    setTimeout(() => {
      const assistantMessage: Message = {
        role: 'assistant',
        content: '这是智能对话的骨架实现，请接入 LLM 服务。',
      }
      setMessages(prev => [...prev, assistantMessage])
      setLoading(false)
    }, 500)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ flex: 1, overflow: 'auto', padding: '16px 0' }}>
        <List
          dataSource={messages}
          renderItem={(msg) => (
            <List.Item style={{ border: 'none', padding: '8px 0' }}>
              <div style={{
                maxWidth: '80%',
                padding: '12px 16px',
                borderRadius: 8,
                backgroundColor: msg.role === 'user' ? '#1890ff' : '#f5f5f5',
                color: msg.role === 'user' ? '#fff' : '#000',
                marginLeft: msg.role === 'user' ? 'auto' : 0,
              }}>
                {msg.content}
              </div>
            </List.Item>
          )}
        />
        {loading && (
          <div style={{ padding: '8px 0', color: '#999' }}>
            <Text type="secondary">正在思考...</Text>
          </div>
        )}
      </div>

      <div style={{ padding: '16px 0', borderTop: '1px solid #f0f0f0' }}>
        <Space.Compact style={{ width: '100%' }}>
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onPressEnter={handleSend}
            placeholder="输入你的问题..."
            size="large"
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSend}
            loading={loading}
            size="large"
          >
            发送
          </Button>
        </Space.Compact>
      </div>
    </div>
  )
}
