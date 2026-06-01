import { useState, useEffect } from 'react'
import { Table, Button, message, Modal, Input, Space, Card, Row, Col, Statistic } from 'antd'
import { PlusOutlined, PlayCircleOutlined } from '@ant-design/icons'
import { evalApi } from '@/api'
import type { EvalExperiment } from '@/types'

export default function Eval() {
  const [experiments, setExperiments] = useState<EvalExperiment[]>([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [expName, setExpName] = useState('')

  const fetchData = async () => {
    setLoading(true)
    try {
      // TODO: 获取实验列表
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
      await evalApi.createExperiment(expName)
      message.success('创建成功')
      setModalOpen(false)
      setExpName('')
      fetchData()
    } catch {
      message.error('创建失败')
    }
  }

  const handleRun = async (id: number) => {
    try {
      await evalApi.runExperiment(id)
      message.success('运行完成')
      fetchData()
    } catch {
      message.error('运行失败')
    }
  }

  const columns = [
    { title: '实验名称', dataIndex: 'name', key: 'name' },
    { title: '状态', dataIndex: 'status', key: 'status' },
    {
      title: 'Faithfulness',
      dataIndex: 'faithfulness',
      key: 'faithfulness',
      render: (v: number | null) => v?.toFixed(3) || '-',
    },
    {
      title: 'Context Precision',
      dataIndex: 'context_precision',
      key: 'context_precision',
      render: (v: number | null) => v?.toFixed(3) || '-',
    },
    {
      title: 'Context Recall',
      dataIndex: 'context_recall',
      key: 'context_recall',
      render: (v: number | null) => v?.toFixed(3) || '-',
    },
    {
      title: 'Answer Relevancy',
      dataIndex: 'answer_relevancy',
      key: 'answer_relevancy',
      render: (v: number | null) => v?.toFixed(3) || '-',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: unknown, record: EvalExperiment) => (
        <Button
          type="link"
          icon={<PlayCircleOutlined />}
          onClick={() => handleRun(record.id)}
        >
          运行
        </Button>
      ),
    },
  ]

  return (
    <div>
      <Button
        type="primary"
        icon={<PlusOutlined />}
        onClick={() => setModalOpen(true)}
        style={{ marginBottom: 16 }}
      >
        创建实验
      </Button>

      <Table columns={columns} dataSource={experiments} loading={loading} rowKey="id" />

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
