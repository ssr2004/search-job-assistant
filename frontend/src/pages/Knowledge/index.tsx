import { useState, useEffect } from 'react'
import { Table, Button, Upload, message, Space, Card, Statistic, Row, Col, Input, List, Tag } from 'antd'
import { UploadOutlined, DeleteOutlined, FileTextOutlined, SearchOutlined } from '@ant-design/icons'
import type { UploadProps } from 'antd'
import { knowledgeApi } from '@/api'
import type { Document, KnowledgeStats } from '@/types'

const { Search } = Input

interface SearchResult {
  id: string
  content: string
  metadata: Record<string, unknown>
  rrf_score?: number
  rerank_score?: number
}

export default function Knowledge() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [stats, setStats] = useState<KnowledgeStats | null>(null)
  const [loading, setLoading] = useState(false)
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])
  const [searching, setSearching] = useState(false)

  const fetchData = async () => {
    setLoading(true)
    try {
      const [docsRes, statsRes] = await Promise.all([
        knowledgeApi.getDocuments(),
        knowledgeApi.getStats(),
      ])
      setDocuments(docsRes.data)
      setStats(statsRes.data)
    } catch {
      message.error('获取数据失败')
    }
    setLoading(false)
  }

  useEffect(() => {
    fetchData()
  }, [])

  const uploadProps: UploadProps = {
    accept: '.pdf,.md,.txt',
    showUploadList: false,
    customRequest: async ({ file, onSuccess, onError }) => {
      try {
        await knowledgeApi.upload(file as File)
        message.success('上传成功')
        onSuccess?.({})
        fetchData()
      } catch {
        message.error('上传失败')
        onError?.(new Error('上传失败'))
      }
    },
  }

  const handleDelete = async (id: number) => {
    try {
      await knowledgeApi.deleteDocument(id)
      message.success('删除成功')
      fetchData()
    } catch {
      message.error('删除失败')
    }
  }

  const handleSearch = async (value: string) => {
    if (!value.trim()) {
      setSearchResults([])
      return
    }
    setSearching(true)
    try {
      const res = await knowledgeApi.search(value)
      setSearchResults(res.data)
    } catch {
      message.error('搜索失败')
    }
    setSearching(false)
  }

  const columns = [
    { title: '文件名', dataIndex: 'filename', key: 'filename' },
    { title: '类型', dataIndex: 'file_type', key: 'file_type' },
    { title: '分块数', dataIndex: 'chunk_count', key: 'chunk_count' },
    { title: '领域', dataIndex: 'domain', key: 'domain' },
    { title: '状态', dataIndex: 'status', key: 'status' },
    {
      title: '操作',
      key: 'action',
      render: (_: unknown, record: Document) => (
        <Button
          type="link"
          danger
          icon={<DeleteOutlined />}
          onClick={() => handleDelete(record.id)}
        >
          删除
        </Button>
      ),
    },
  ]

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card>
            <Statistic
              title="文档总数"
              value={stats?.total_documents || 0}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="分块总数" value={stats?.total_chunks || 0} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="领域数量" value={stats?.domains?.length || 0} />
          </Card>
        </Col>
      </Row>

      <Card title="知识库检索" style={{ marginBottom: 24 }}>
        <Search
          placeholder="输入关键词搜索知识库..."
          enterButton={<><SearchOutlined /> 搜索</>}
          size="large"
          loading={searching}
          onSearch={handleSearch}
        />
        {searchResults.length > 0 && (
          <List
            style={{ marginTop: 16 }}
            header={<div>找到 {searchResults.length} 条相关结果</div>}
            dataSource={searchResults}
            renderItem={(item) => (
              <List.Item>
                <List.Item.Meta
                  title={
                    <Space>
                      <Tag color="blue">{(item.metadata as Record<string, unknown>)?.source as string}</Tag>
                      {item.rerank_score && <Tag color="green">相关度: {(item.rerank_score as number).toFixed(3)}</Tag>}
                    </Space>
                  }
                  description={item.content}
                />
              </List.Item>
            )}
          />
        )}
      </Card>

      <Card title="文档管理">
        <div style={{ marginBottom: 16 }}>
          <Upload {...uploadProps}>
            <Button type="primary" icon={<UploadOutlined />}>
              上传文档
            </Button>
          </Upload>
        </div>

        <Table
          columns={columns}
          dataSource={documents}
          loading={loading}
          rowKey="id"
        />
      </Card>
    </div>
  )
}
