import { useState, useEffect } from 'react'
import { Table, Button, message, Modal, Input, Card, Row, Col, Statistic, Tag } from 'antd'
import { PlusOutlined, PlayCircleOutlined, CheckCircleOutlined } from '@ant-design/icons'
import { evalApi } from '@/api'
import type { EvalExperiment } from '@/types'

export default function Eval() {
  const [experiments, setExperiments] = useState<EvalExperiment[]>([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [expName, setExpName] = useState('')
  const [selectedExp, setSelectedExp] = useState<EvalExperiment | null>(null)

  const fetchData = async () => {
    setLoading(true)
    try {
      // 由于后端没有列表接口，使用空数组
      setExperiments([])
    } catch {
      message.error('获取数据失败')
    }
    setLoading(false)
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleCreate = async () => {
    if (!expName) {
      message.warning('请输入实验名称')
      return
    }
    try {
      const res = await evalApi.createExperiment(expName)
      message.success('创建成功')
      setModalOpen(false)
      setExpName('')
      setSelectedExp(res.data)
    } catch {
      message.error('创建失败')
    }
  }

  const handleRun = async () => {
    if (!selectedExp) {
      message.warning('请先创建实验')
      return
    }
    try {
      message.loading('正在运行评估...')
      const res = await evalApi.runExperiment(selectedExp.id)
      setSelectedExp(res.data)
      message.success('评估完成')
    } catch {
      message.error('运行失败')
    }
  }

  return (
    <div>
      <Card title="RAGAS 评估" style={{ marginBottom: 24 }}>
        <p>RAGAS 是一个评估 RAG 系统的框架，包含四个指标：</p>
        <ul>
          <li><strong>Faithfulness（忠实度）</strong>：回答是否基于检索到的上下文</li>
          <li><strong>Context Precision（上下文精确度）</strong>：检索到的上下文是否相关</li>
          <li><strong>Context Recall（上下文召回率）</strong>：相关上下文是否被检索到</li>
          <li><strong>Answer Relevancy（回答相关性）</strong>：回答是否与问题相关</li>
        </ul>

        <div style={{ marginTop: 16 }}>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setModalOpen(true)}
            style={{ marginRight: 16 }}
          >
            创建实验
          </Button>
          <Button
            icon={<PlayCircleOutlined />}
            onClick={handleRun}
            disabled={!selectedExp}
          >
            运行评估
          </Button>
        </div>
      </Card>

      {selectedExp && (
        <Card title={`实验: ${selectedExp.name}`}>
          <Row gutter={16}>
            <Col span={6}>
              <Statistic
                title="Faithfulness"
                value={selectedExp.faithfulness?.toFixed(3) || '-'}
                suffix={selectedExp.faithfulness ? <CheckCircleOutlined style={{ color: '#52c41a' }} /> : null}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="Context Precision"
                value={selectedExp.context_precision?.toFixed(3) || '-'}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="Context Recall"
                value={selectedExp.context_recall?.toFixed(3) || '-'}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="Answer Relevancy"
                value={selectedExp.answer_relevancy?.toFixed(3) || '-'}
              />
            </Col>
          </Row>

          <div style={{ marginTop: 16 }}>
            <Tag color={selectedExp.status === 'completed' ? 'green' : 'blue'}>
              {selectedExp.status}
            </Tag>
          </div>
        </Card>
      )}

      <Modal
        title="创建评估实验"
        open={modalOpen}
        onOk={handleCreate}
        onCancel={() => setModalOpen(false)}
      >
        <Input
          placeholder="实验名称"
          value={expName}
          onChange={(e) => setExpName(e.target.value)}
        />
      </Modal>
    </div>
  )
}
