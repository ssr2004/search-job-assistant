import { useState, useEffect } from 'react'
import { Tabs, Table, Button, Upload, message, Modal, Input, Card, Space, Select, Progress, Tag } from 'antd'
import { UploadOutlined, PlusOutlined, ThunderboltOutlined } from '@ant-design/icons'
import type { UploadProps } from 'antd'
import { resumeApi, jdApi, matchApi, gapApi } from '@/api'
import type { Resume, JobDescription, MatchResult, GapAnalysis } from '@/types'

const { TextArea } = Input

export default function Resume() {
  const [resumes, setResumes] = useState<Resume[]>([])
  const [jds, setJds] = useState<JobDescription[]>([])
  const [matchResults, setMatchResults] = useState<MatchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [jdModalOpen, setJdModalOpen] = useState(false)
  const [jdTitle, setJdTitle] = useState('')
  const [jdText, setJdText] = useState('')
  const [matchModalOpen, setMatchModalOpen] = useState(false)
  const [selectedResume, setSelectedResume] = useState<number>()
  const [selectedJD, setSelectedJD] = useState<number>()
  const [gapAnalysis, setGapAnalysis] = useState<GapAnalysis | null>(null)

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

  const handleMatch = async () => {
    if (!selectedResume || !selectedJD) {
      message.warning('请选择简历和 JD')
      return
    }
    try {
      await matchApi.run(selectedResume, selectedJD)
      message.success('匹配完成')
      setMatchModalOpen(false)
      fetchData()
    } catch {
      message.error('匹配失败')
    }
  }

  const handleGapAnalysis = async () => {
    if (!selectedResume || !selectedJD) {
      message.warning('请选择简历和 JD')
      return
    }
    try {
      const res = await gapApi.analyze(selectedResume, selectedJD)
      setGapAnalysis(res.data)
    } catch {
      message.error('分析失败')
    }
  }

  const resumeColumns = [
    { title: 'ID', dataIndex: 'id', key: 'id' },
    { title: '文件名', dataIndex: 'filename', key: 'filename' },
    { title: '上传时间', dataIndex: 'created_at', key: 'created_at' },
  ]

  const jdColumns = [
    { title: 'ID', dataIndex: 'id', key: 'id' },
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
      render: (score: number) => (
        <Tag color={score >= 0.7 ? 'green' : score >= 0.4 ? 'orange' : 'red'}>
          {(score * 100).toFixed(1)}%
        </Tag>
      ),
    },
    {
      title: '硬性条件',
      dataIndex: 'hard_score',
      key: 'hard_score',
      render: (score: number) => (score * 100).toFixed(1) + '%',
    },
    {
      title: '技能匹配',
      dataIndex: 'skill_score',
      key: 'skill_score',
      render: (score: number) => (score * 100).toFixed(1) + '%',
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
      label: '匹配分析',
      children: (
        <>
          <Card style={{ marginBottom: 16 }}>
            <Space>
              <Select
                placeholder="选择简历"
                style={{ width: 200 }}
                value={selectedResume}
                onChange={setSelectedResume}
                options={resumes.map(r => ({ value: r.id, label: r.filename }))}
              />
              <Select
                placeholder="选择 JD"
                style={{ width: 200 }}
                value={selectedJD}
                onChange={setSelectedJD}
                options={jds.map(j => ({ value: j.id, label: j.title }))}
              />
              <Button type="primary" onClick={handleMatch}>
                执行匹配
              </Button>
              <Button icon={<ThunderboltOutlined />} onClick={handleGapAnalysis}>
                差距分析
              </Button>
            </Space>
          </Card>

          {gapAnalysis && (
            <Card title="技能差距分析" style={{ marginBottom: 16 }}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>
                  <div>必须技能匹配率</div>
                  <Progress percent={Math.round(gapAnalysis.required_match_rate * 100)} status="active" />
                </div>
                <div>
                  <div>加分技能匹配率</div>
                  <Progress percent={Math.round(gapAnalysis.preferred_match_rate * 100)} status="active" />
                </div>
                <div>
                  <div>已掌握技能：</div>
                  {gapAnalysis.matched_required.map(s => <Tag color="green" key={s}>{s}</Tag>)}
                </div>
                <div>
                  <div>缺失技能：</div>
                  {gapAnalysis.missing_required.map(s => <Tag color="red" key={s}>{s}</Tag>)}
                </div>
              </Space>
            </Card>
          )}

          <Table columns={matchColumns} dataSource={matchResults} loading={loading} rowKey="id" />
        </>
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
