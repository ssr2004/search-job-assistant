import { useState, useEffect } from 'react'
import { Card, Button, Select, message, Row, Col, Progress, List, Tag, Space } from 'antd'
import { ThunderboltOutlined } from '@ant-design/icons'
import { gapApi, resumeApi, jdApi } from '@/api'
import type { GapAnalysis, Resume, JobDescription } from '@/types'

export default function Gap() {
  const [analysis, setAnalysis] = useState<GapAnalysis | null>(null)
  const [loading, setLoading] = useState(false)
  const [resumeId, setResumeId] = useState<number | undefined>()
  const [jdId, setJdId] = useState<number | undefined>()
  const [resumes, setResumes] = useState<Resume[]>([])
  const [jds, setJds] = useState<JobDescription[]>([])

  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const [resumesRes, jdsRes] = await Promise.all([
          resumeApi.list(),
          jdApi.list(),
        ])
        setResumes(resumesRes.data)
        setJds(jdsRes.data)
      } catch {
        // 忽略错误
      }
    }
    fetchOptions()
  }, [])

  const handleAnalyze = async () => {
    if (!resumeId || !jdId) {
      message.warning('请选择简历和 JD')
      return
    }
    setLoading(true)
    try {
      const res = await gapApi.analyze(resumeId, jdId)
      setAnalysis(res.data)
    } catch {
      message.error('分析失败')
    }
    setLoading(false)
  }

  return (
    <div>
      <Card style={{ marginBottom: 24 }}>
        <Space>
          <Select
            placeholder="选择简历"
            style={{ width: 200 }}
            value={resumeId}
            onChange={setResumeId}
            options={resumes.map(r => ({ value: r.id, label: r.filename }))}
          />
          <Select
            placeholder="选择 JD"
            style={{ width: 200 }}
            value={jdId}
            onChange={setJdId}
            options={jds.map(j => ({ value: j.id, label: j.title }))}
          />
          <Button
            type="primary"
            icon={<ThunderboltOutlined />}
            onClick={handleAnalyze}
            loading={loading}
          >
            分析差距
          </Button>
        </Space>
      </Card>

      {analysis && (
        <>
          <Row gutter={16} style={{ marginBottom: 24 }}>
            <Col span={8}>
              <Card>
                <Progress
                  type="circle"
                  percent={Math.round(analysis.required_match_rate * 100)}
                  format={(percent) => `${percent}%`}
                />
                <div style={{ textAlign: 'center', marginTop: 8 }}>必须技能匹配率</div>
              </Card>
            </Col>
            <Col span={8}>
              <Card>
                <Progress
                  type="circle"
                  percent={Math.round(analysis.preferred_match_rate * 100)}
                  format={(percent) => `${percent}%`}
                />
                <div style={{ textAlign: 'center', marginTop: 8 }}>加分技能匹配率</div>
              </Card>
            </Col>
            <Col span={8}>
              <Card>
                <Progress
                  type="circle"
                  percent={Math.round(analysis.overall_match_rate * 100)}
                  format={(percent) => `${percent}%`}
                />
                <div style={{ textAlign: 'center', marginTop: 8 }}>综合匹配率</div>
              </Card>
            </Col>
          </Row>

          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={12}>
              <Card title="已掌握的必须技能">
                {analysis.matched_required.length > 0 ? (
                  analysis.matched_required.map((skill) => (
                    <Tag color="green" key={skill}>{skill}</Tag>
                  ))
                ) : (
                  <span style={{ color: '#999' }}>无</span>
                )}
              </Card>
            </Col>
            <Col span={12}>
              <Card title="缺失的必须技能">
                {analysis.missing_required.length > 0 ? (
                  analysis.missing_required.map((skill) => (
                    <Tag color="red" key={skill}>{skill}</Tag>
                  ))
                ) : (
                  <span style={{ color: '#52c41a' }}>全部掌握！</span>
                )}
              </Card>
            </Col>
          </Row>

          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={12}>
              <Card title="已掌握的加分技能">
                {analysis.matched_preferred.length > 0 ? (
                  analysis.matched_preferred.map((skill) => (
                    <Tag color="green" key={skill}>{skill}</Tag>
                  ))
                ) : (
                  <span style={{ color: '#999' }}>无</span>
                )}
              </Card>
            </Col>
            <Col span={12}>
              <Card title="缺失的加分技能">
                {analysis.missing_preferred.length > 0 ? (
                  analysis.missing_preferred.map((skill) => (
                    <Tag color="orange" key={skill}>{skill}</Tag>
                  ))
                ) : (
                  <span style={{ color: '#52c41a' }}>全部掌握！</span>
                )}
              </Card>
            </Col>
          </Row>

          <Card title="学习推荐">
            <List
              dataSource={analysis.recommendations}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    title={item.skill as string || '推荐'}
                    description={item.message as string || JSON.stringify(item)}
                  />
                  {item.priority && (
                    <Tag color={item.priority === '高' ? 'red' : item.priority === '中' ? 'orange' : 'blue'}>
                      {item.priority as string}
                    </Tag>
                  )}
                </List.Item>
              )}
            />
          </Card>
        </>
      )}
    </div>
  )
}
