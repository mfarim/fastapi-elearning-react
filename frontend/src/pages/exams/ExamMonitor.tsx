import React, { useEffect, useState, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../../api/client';
import type { Exam, ExamMonitorItem, ApiResponse } from '../../types';
import {
  ArrowLeft,
  MonitorPlay,
  Users,
  AlertTriangle,
  CheckCircle2,
  Radio,
  RefreshCw,
} from 'lucide-react';

export const ExamMonitor: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [exam, setExam] = useState<Exam | null>(null);
  const [attempts, setAttempts] = useState<ExamMonitorItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [wsConnected, setWsConnected] = useState(false);
  const [recentAlert, setRecentAlert] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const [eRes, mRes] = await Promise.all([
        api.get<ApiResponse<Exam>>(`/exams/${id}`),
        api.get<ApiResponse<ExamMonitorItem[]>>(`/exams/${id}/monitor`),
      ]);
      setExam(eRes.data.data);
      setAttempts(mRes.data.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!id) return;
    loadData();

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/exams/${id}/monitor`;

    let reconnectTimer: any = null;

    const connectWebSocket = () => {
      try {
        const socket = new WebSocket(wsUrl);

        socket.onopen = () => {
          setWsConnected(true);
        };

        socket.onmessage = (event) => {
          try {
            const parsed = JSON.parse(event.data);
            handleRealtimeEvent(parsed);
          } catch (e) {
            console.error('Error handling WS event', e);
          }
        };

        socket.onclose = () => {
          setWsConnected(false);
          reconnectTimer = setTimeout(connectWebSocket, 4000);
        };

        socket.onerror = () => {
          socket.close();
        };

        wsRef.current = socket;
      } catch {
        setWsConnected(false);
        reconnectTimer = setTimeout(connectWebSocket, 4000);
      }
    };

    connectWebSocket();

    // Fallback polling every 8s
    const pollInterval = setInterval(() => {
      loadData();
    }, 8000);

    return () => {
      if (reconnectTimer) clearTimeout(reconnectTimer);
      clearInterval(pollInterval);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [id]);

  const handleRealtimeEvent = (event: any) => {
    const { eventType, data } = event;

    if (eventType === 'VIOLATION_REPORTED') {
      setRecentAlert(`🚨 VIOLATION: Student ${data.studentName} flagged for ${data.violationType || data.notes || 'anti-cheat violation'}!`);
      setTimeout(() => setRecentAlert(null), 6000);

      setAttempts((prev) =>
        prev.map((att) =>
          att.attemptId === (data.attemptId || data.attempt_id) || att.studentId === (data.studentId || data.student_id)
            ? { ...att, violations: data.violations }
            : att
        )
      );
    } else if (eventType === 'ANSWER_SAVED') {
      setAttempts((prev) =>
        prev.map((att) =>
          att.attemptId === (data.attemptId || data.attempt_id) || att.studentId === (data.studentId || data.student_id)
            ? { ...att, answeredCount: Math.min((att.answeredCount || 0) + 1, att.totalQuestions) }
            : att
        )
      );
    } else if (eventType === 'STUDENT_ENTERED') {
      loadData();
    } else if (eventType === 'EXAM_SUBMITTED') {
      setAttempts((prev) =>
        prev.map((att) =>
          att.attemptId === (data.attemptId || data.attempt_id) || att.studentId === (data.studentId || data.student_id)
            ? { ...att, status: data.status || 'completed', score: data.score }
            : att
        )
      );
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'in_progress':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800 animate-pulse">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
            Sedang Mengerjakan
          </span>
        );
      case 'completed':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Selesai
          </span>
        );
      case 'needs_grading':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
            Perlu Penilaian
          </span>
        );
      case 'force_finished':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-rose-100 text-rose-800">
            Dihentikan Paksa
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
            {status}
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header & Breadcrumb */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Link
              to="/exams"
              className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-emerald-600 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" /> Kembali ke Daftar Ujian
            </Link>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
            <MonitorPlay className="w-7 h-7 text-emerald-600" />
            Ruang Pengawas Real-Time CBT
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Ujian: <strong className="text-gray-900">{exam?.title || 'Memuat...'}</strong> | Kelas:{' '}
            <strong className="text-gray-900">{exam?.classroomName || '-'}</strong>
          </p>
        </div>

        {/* Live Status indicator */}
        <div className="flex items-center gap-3">
          <button
            onClick={loadData}
            disabled={loading}
            className="p-2 text-gray-600 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors border border-gray-200"
            title="Refresh Data"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>

          <div
            className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold ${
              wsConnected
                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                : 'bg-rose-50 text-rose-700 border border-rose-200'
            }`}
          >
            <Radio className={`w-3.5 h-3.5 ${wsConnected ? 'animate-pulse text-emerald-600' : 'text-rose-600'}`} />
            {wsConnected ? 'Live WebSocket Terhubung' : 'WebSocket Terputus (Mode Polling)'}
          </div>
        </div>
      </div>

      {/* Floating Alert on Anti-Cheat Violation */}
      {recentAlert && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 flex items-center justify-between shadow-sm animate-bounce">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-rose-600 flex-shrink-0" />
            <span className="font-semibold text-sm">{recentAlert}</span>
          </div>
          <button
            onClick={() => setRecentAlert(null)}
            className="text-xs text-rose-600 hover:underline font-medium"
          >
            Tutup
          </button>
        </div>
      )}

      {/* Overview Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm">
          <p className="text-xs font-medium text-gray-500">Total Peserta Terdaftar</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{attempts.length}</p>
        </div>
        <div className="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm">
          <p className="text-xs font-medium text-gray-500">Sedang Ujian Aktif</p>
          <p className="text-2xl font-bold text-emerald-600 mt-1">
            {attempts.filter((a) => a.status === 'in_progress').length}
          </p>
        </div>
        <div className="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm">
          <p className="text-xs font-medium text-gray-500">Telah Mengumpulkan</p>
          <p className="text-2xl font-bold text-blue-600 mt-1">
            {attempts.filter((a) => a.status === 'completed' || a.status === 'needs_grading').length}
          </p>
        </div>
        <div className="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm">
          <p className="text-xs font-medium text-gray-500">Total Pelanggaran Terdeteksi</p>
          <p className="text-2xl font-bold text-rose-600 mt-1">
            {attempts.reduce((sum, a) => sum + (a.violations || 0), 0)}
          </p>
        </div>
      </div>

      {/* Student Session Progress Table */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-5 border-b border-gray-100 flex items-center justify-between">
          <h2 className="font-bold text-gray-900 flex items-center gap-2">
            <Users className="w-5 h-5 text-gray-500" />
            Status Pengerjaan Peserta Ujian
          </h2>
          <span className="text-xs text-gray-500">Diperbarui secara real-time via telemetri</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-600">
            <thead className="bg-gray-50 text-gray-500 font-medium text-xs uppercase tracking-wider">
              <tr>
                <th className="px-6 py-3">Nama Siswa</th>
                <th className="px-6 py-3">NIS</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Progres Soal</th>
                <th className="px-6 py-3">Pelanggaran</th>
                <th className="px-6 py-3">Nilai</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {attempts.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-gray-400">
                    Belum ada siswa yang memulai ujian ini.
                  </td>
                </tr>
              ) : (
                attempts.map((att) => {
                  const progressPct =
                    att.totalQuestions > 0
                      ? Math.round(((att.answeredCount || 0) / att.totalQuestions) * 100)
                      : 0;

                  return (
                    <tr key={att.attemptId} className="hover:bg-gray-50/60 transition-colors">
                      <td className="px-6 py-4 font-semibold text-gray-900">{att.studentName}</td>
                      <td className="px-6 py-4 text-gray-500 font-mono text-xs">{att.nis}</td>
                      <td className="px-6 py-4">{getStatusBadge(att.status)}</td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-24 bg-gray-200 h-2 rounded-full overflow-hidden">
                            <div
                              className="bg-emerald-600 h-full rounded-full transition-all duration-300"
                              style={{ width: `${progressPct}%` }}
                            ></div>
                          </div>
                          <span className="text-xs font-medium text-gray-600">
                            {att.answeredCount || 0} / {att.totalQuestions} ({progressPct}%)
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        {att.violations > 0 ? (
                          <span className="inline-flex items-center gap-1 font-bold text-rose-600 bg-rose-50 px-2 py-0.5 rounded text-xs">
                            <AlertTriangle className="w-3.5 h-3.5" />
                            {att.violations}x Pelanggaran
                          </span>
                        ) : (
                          <span className="text-xs text-gray-400">0</span>
                        )}
                      </td>
                      <td className="px-6 py-4 font-bold text-gray-900">
                        {att.score !== null && att.score !== undefined ? (
                          <span className={att.score >= (exam?.passingScore || 75) ? 'text-emerald-600' : 'text-rose-600'}>
                            {att.score}
                          </span>
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
