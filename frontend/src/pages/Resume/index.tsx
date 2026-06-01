import { useState, useEffect } from 'react'
import { Tabs, Table, Button, Upload, message, Modal, Input, Card, Space } from 'antd'
import { UploadOutlined, PlusOutlined } from '@ant-design/icons'
import type { UploadProps } from 'antd'
import { resumeApi, jdApi, matchApi } from '@/api'
import type { Resume, JobDescription, MatchResult } from '@/types'

const { TextArea } = Input

export default function Resume() {
  const [resumes, setResumes] = useState<Resume[]>([])
  const [jds, setJds] = useState<JobDescription[]>([])
  const [matchResults, setMatchResults] = useState<MatchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [jdModalOpen, setJdModalOpen] = useState(false)
  const [jdTitle, setJdTitle] = useState('')
  const [jdText, setJdText] = useState('')

  const fetchData = async () => {
    setLoading(true)
    try {
      const [resumesRes, jdsRes, matchRes] = await Promise.all([
        resumeApi.list(),
        jdApi.list(),
        matchApi.getResults(),
      ])
      setResumes(resumesRes.data)
      setJds(jdsRes.data)
      setMatchResults(matchRes.data)
    } catch {
      message.error('获取数据失败')
    }
    setLoading(false)
  }

  useEffect(() => {
    fetchData()
  }, [])

  const uploadResumeProps: UploadProps = {
    accept: '.pdf,.docx,.txt',
    showUploadList: false,
    customRequest: async ({ file, onSuccess, onError }) => {
      try {
        await resumeApi.upload(file as File)
        message.success('上传成功')
        onSuccess?.({})
        fetchData()
      } catch {
        message.error('上传失败')
        onError?.(new Error('上传失败'))
      }
    },
  }

  const handleCreateJD = async () => {
    if (!jdTitle || !jdText) {
      message.warning('请填写完整')
      return
    }
    try {
      await jdApi.create(jdTitle, jdText)
      message.success('创建成功')
      setJdModalOpen(false)
      setJdTitle('')
      setJdText('')
      fetchData()
    } catch {
      message.error('创建失败')
    }
  }

  const handleMatch = async (resumeId: number, jdId: number) => {
    try {
      await matchApi.run(resumeId, jdId)
      message.success('匹配完成')
      fetchData()
    } catch {
      message.error('匹配失败')
    }
  }

  const resumeColumns = [
    { title: '文件名', dataIndex: 'filename', key: 'filename' },
    { title: '上传时间', dataIndex: 'created_at', key: 'created_at' },
  ]

  const jdColumns = [
    { title: '职位', dataIndex: 'title', key: 'title' },
    { title: '创建时间', dataIndex: 'created_at', key: 'created_at' },
  ]

  const matchColumns = [
    { title: '简历ID', dataIndex: 'resume_id', key: 'resume_id' },
    { title: 'JD ID', dataIndex: 'jd_id', key: 'jd_id' },
    {
      title: '综合评分',
      dataIndex: 'final_score',
      key: 'final_score',
      render: (score: number) => (score * 100).toFixed(1) + '%',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: unknown, record: MatchResult) => (
        <Button type="link" onClick={() => handleMatch(record.resume_id, record.jd_id)}>
          重新匹配
        </Button>
      ),
    },
  ]

  const tabItems = [
    {
      key: 'resume',
      label: '简历管理',
      children: (
        <>
          <Upload {...uploadResumeProps}>
            <Button type="primary" icon={<UploadOutlined />} style={{ marginBottom: 16 }}>
              上传简历
            </Button>
          </Upload>
          <Table columns={resumeColumns} dataSource={resumes} loading={loading} rowKey="id" />
        </>
      ),
    },
    {
      key: 'jd',
      label: 'JD 管理',
      children: (
        <>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setJdModalOpen(true)}
            style={{ marginBottom: 16 }}
          >
            创建 JD
          </Button>
          <Table columns={jdColumns} dataSource={jds} loading={loading} rowKey="id" />
        </>
      ),
    },
    {
      key: 'match',
      label: '匹配结果',
      children: (
        <Table columns={matchColumns} dataSource={matchResults} loading={loading} rowKey="id" />
      ),
    },
  ]

  return (
    <div>
      <Tabs items={tabItems} />

      <Modal
        title="创建 JD"
        open={jdModalOpen}
        onOk={handleCreateJD}
        onCancel={() => setJdModalOpen(false)}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <Input
            placeholder="职位名称"
            value={jdTitle}
            onChange={(e) => setJdTitle(e.target.value)}
          />
          <TextArea
            placeholder="JD 内容"
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
            rows={10}
          />
        </Space>
      </Modal>
    </div>
  )
}
