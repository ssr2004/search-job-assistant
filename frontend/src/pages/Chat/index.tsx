import { useState, useRef, useEffect } from 'react'
import { Input, Button, List, Typography, Space, Select, Card, message } from 'antd'
import { SendOutlined, RobotOutlined, UserOutlined } from '@ant-design/icons'
import { chatApi } from '@/api'
import ReactMarkdown from 'react-markdown'

const { Text } = Typography

interface Message {
  role: 'user' | 'assistant'
  content: string
}

const domains = [
  { value: '', label: '通用' },
  { value: 'java', label: 'Java' },
  { value: 'python', label: 'Python' },
  { value: 'ai', label: 'AI/ML' },
  { value: 'frontend', label: '前端' },
  { value: 'backend', label: '后端' },
]

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [domain, setDomain] = useState('')
  const [sessionId] = useState(() => `session_${Date.now()}`)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage: Message = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await chatApi.stream(sessionId, userMessage.content, domain || undefined)

      if (!response.ok) {
        throw new Error('请求失败')
      }

      const reader = response.body?.getReader()
      if (!reader) throw new Error('无法读取响应')

      const decoder = new TextDecoder()
      let assistantContent = ''

      // 添加空的助手消息
      setMessages(prev => [...prev, { role: 'assistant', content: '' }])

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const text = decoder.decode(value)
        const lines = text.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') continue

            try {
              const parsed = JSON.parse(data)
              assistantContent += parsed.content
              // 更新最后一条消息
              setMessages(prev => {
                const newMessages = [...prev]
                newMessages[newMessages.length - 1] = {
                  role: 'assistant',
                  content: assistantContent
                }
                return newMessages
              })
            } catch {
              // 忽略解析错误
            }
          }
        }
      }
    } catch (error) {
      message.error('发送失败')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ marginBottom: 16 }}>
        <Space>
          <Text>领域：</Text>
          <Select
            value={domain}
            onChange={setDomain}
            options={domains}
            style={{ width: 120 }}
            placeholder="选择领域"
          />
        </Space>
      </div>

      <Card style={{ flex: 1, overflow: 'auto', marginBottom: 16 }}>
        <div style={{ minHeight: 400 }}>
          {messages.length === 0 && (
            <div style={{ textAlign: 'center', color: '#999', padding: '100px 0' }}>
              <RobotOutlined style={{ fontSize: 48, marginBottom: 16 }} />
              <div>你好！我是智能求职助手，有什么可以帮你的？</div>
            </div>
          )}
          {messages.map((msg, index) => (
            <div
              key={index}
              style={{
                display: 'flex',
                justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                marginBottom: 16,
              }}
            >
              <div style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: 8,
                maxWidth: '80%',
                flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
              }}>
                <div style={{
                  width: 32,
                  height: 32,
                  borderRadius: '50%',
                  backgroundColor: msg.role === 'user' ? '#1890ff' : '#52c41a',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#fff',
                  flexShrink: 0,
                }}>
                  {msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                </div>
                <div style={{
                  padding: '12px 16px',
                  borderRadius: 8,
                  backgroundColor: msg.role === 'user' ? '#1890ff' : '#f5f5f5',
                  color: msg.role === 'user' ? '#fff' : '#000',
                }}>
                  {msg.role === 'assistant' ? (
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  ) : (
                    msg.content
                  )}
                </div>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </Card>

      <div>
        <Space.Compact style={{ width: '100%' }}>
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onPressEnter={handleSend}
            placeholder="输入你的问题..."
            size="large"
            disabled={loading}
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
