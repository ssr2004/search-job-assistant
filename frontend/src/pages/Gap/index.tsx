import { useState } from 'react'
import { Card, Button, Select, message, Row, Col, Progress, List, Tag, Space } from 'antd'
import { ThunderboltOutlined } from '@ant-design/icons'
import { gapApi, resumeApi, jdApi } from '@/api'
import type { GapAnalysis } from '@/types'

export default function Gap() {
  const [analysis, setAnalysis] = useState<GapAnalysis | null>(null)
  const [loading, setLoading] = useState(false)
  const [resumeId, setResumeId] = useState<number | undefined>()
  const [jdId, setJdId] = useState<number | undefined>()

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
            onChange={(v) => setResumeId(v)}
            options={[]}
          />
          <Select
            placeholder="选择 JD"
            style={{ width: 200 }}
            onChange={(v) => setJdId(v)}
            options={[]}
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

          <Row gutter={16}>
            <Col span={12}>
              <Card title="已掌握的必须技能">
                {analysis.matched_required.map((skill) => (
                  <Tag color="green" key={skill}>{skill}</Tag>
                ))}
              </Card>
            </Col>
            <Col span={12}>
              <Card title="缺失的必须技能">
                {analysis.missing_required.map((skill) => (
                  <Tag color="red" key={skill}>{skill}</Tag>
                ))}
              </Card>
            </Col>
          </Row>

          <Card title="学习推荐" style={{ marginTop: 16 }}>
            <List
              dataSource={analysis.recommendations}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    title={item.skill as string || '推荐'}
                    description={item.message as string || JSON.stringify(item)}
                  />
                </List.Item>
              )}
            />
          </Card>
        </>
      )}
    </div>
  )
}
