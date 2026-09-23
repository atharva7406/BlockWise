import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import DemoControlBar from './components/DemoControlBar';
import TopologyView from './components/TopologyView';
import TaskListView from './components/TaskListView';
import BundleView from './components/BundleView';
import ScheduleGanttView from './components/ScheduleGanttView';
import PriorityBreakdownView from './components/PriorityBreakdownView';
import OfficerActionModal from './components/OfficerActionModal';
import CanonicalContractsModal from './components/CanonicalContractsModal';
import HonestyPointsModal from './components/HonestyPointsModal';
import {
  fetchTasks,
  setPolicyMode,
  fetchBundles,
  fetchSchedule,
  solveSchedule,
  submitOfficerAction,
  triggerEmergency,
  toggleTdms,
  resetDemo,
} from './services/api';
import { Layers, ListChecks, GitMerge, Calendar, AlertCircle } from 'lucide-react';

export default function App() {
  const [tasks, setTasks] = useState([]);
  const [bundles, setBundles] = useState([]);
  const [scheduleData, setScheduleData] = useState({ schedule: [], stats: {} });
  const [policyMode, setPolicyModeState] = useState("Balanced");
  const [tdmsOnline, setTdmsOnline] = useState(true);
  const [activeTab, setActiveTab] = useState("topology"); // topology, tasks, bundles, schedule
  const [selectedTask, setSelectedTask] = useState(null);
  const [actionBlock, setActionBlock] = useState(null);
  const [showContractsModal, setShowContractsModal] = useState(false);
  const [showQAModal, setShowQAModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState(null);

  const showNotification = (msg, type = "info") => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 5000);
  };

  const loadData = async () => {
    try {
      setLoading(true);
      const [tList, bList, sData] = await Promise.all([
        fetchTasks(),
        fetchBundles(),
        fetchSchedule(),
      ]);
      setTasks(tList);
      setBundles(bList);
      setScheduleData(sData);
    } catch (err) {
      console.error(err);
      showNotification("Could not connect to backend server on localhost:8000. Ensure FastAPI is running.", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handlePolicyChange = async (newMode) => {
    setPolicyModeState(newMode);
    try {
      await setPolicyMode(newMode);
      await loadData();
      showNotification(`Policy mode switched to "${newMode}". Priority scores recalibrated.`, "success");
    } catch (err) {
      console.error(err);
    }
  };

  const handleEmergency = async () => {
    try {
      setLoading(true);
      const res = await triggerEmergency();
      await loadData();
      setActiveTab("schedule");
      showNotification(`EMERGENCY INJECTED: Broken rail task ${res.task.task_id} prioritized. Already-approved blocks stayed FROZEN!`, "emergency");
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleTdms = async () => {
    try {
      setLoading(true);
      const res = await toggleTdms();
      setTdmsOnline(res.tdms_online);
      await loadData();
      showNotification(
        res.tdms_online ? "TDMS Telemetry restored." : "TDMS Offline simulated: S&T tasks transitioned to STALE with reduced confidence.",
        "warning"
      );
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleResolveSchedule = async () => {
    try {
      setLoading(true);
      const res = await solveSchedule();
      setScheduleData(res);
      showNotification(`CP-SAT Solved: ${res.stats.scheduled_count} tasks assigned (${res.stats.bundled_count} bundled, ${res.stats.frozen_count || 0} frozen).`, "success");
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    try {
      setLoading(true);
      await resetDemo();
      setTdmsOnline(true);
      await loadData();
      showNotification("Demo scenario reset to baseline.", "info");
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleOfficerSubmit = async (payload) => {
    try {
      await submitOfficerAction(payload);
      await loadData();
      showNotification(`Statutory block order recorded: ${payload.action} for ${payload.task_id}. Block is now LOCKED/FROZEN.`, "success");
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navigation */}
      <Navbar
        policyMode={policyMode}
        onPolicyChange={handlePolicyChange}
        taskCount={tasks.length}
        onOpenContracts={() => setShowContractsModal(true)}
        onOpenQA={() => setShowQAModal(true)}
      />

      {/* Live Demo Controller */}
      <DemoControlBar
        onEmergency={handleEmergency}
        onToggleTdms={handleToggleTdms}
        tdmsOnline={tdmsOnline}
        onResolveSchedule={handleResolveSchedule}
        onReset={handleReset}
        loading={loading}
      />

      {/* Notification Toast */}
      {notification && (
        <div className="px-6 py-2">
          <div
            className={`max-w-7xl mx-auto p-3 rounded-xl border text-xs font-semibold flex items-center space-x-2 animate-fadeIn ${
              notification.type === "emergency"
                ? "bg-red-950/90 border-red-500 text-red-200"
                : notification.type === "warning"
                ? "bg-amber-950/90 border-amber-500 text-amber-200"
                : notification.type === "error"
                ? "bg-red-950/90 border-red-600 text-red-200"
                : "bg-blue-950/90 border-blue-500 text-blue-200"
            }`}
          >
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{notification.msg}</span>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-6 space-y-6">
        {/* Navigation Tabs */}
        <div className="flex border-b border-slate-800 space-x-2 overflow-x-auto pb-1">
          <button
            onClick={() => setActiveTab("topology")}
            className={`flex items-center space-x-2 py-2.5 px-4 rounded-xl text-xs font-bold transition-all ${
              activeTab === "topology"
                ? "bg-blue-600 text-white shadow"
                : "text-slate-400 hover:text-white hover:bg-slate-900"
            }`}
          >
            <Layers className="w-4 h-4" />
            <span>1. Corridor Spatial Topology</span>
          </button>

          <button
            onClick={() => setActiveTab("tasks")}
            className={`flex items-center space-x-2 py-2.5 px-4 rounded-xl text-xs font-bold transition-all ${
              activeTab === "tasks"
                ? "bg-blue-600 text-white shadow"
                : "text-slate-400 hover:text-white hover:bg-slate-900"
            }`}
          >
            <ListChecks className="w-4 h-4" />
            <span>2. Task Registry & Health Gate</span>
          </button>

          <button
            onClick={() => setActiveTab("bundles")}
            className={`flex items-center space-x-2 py-2.5 px-4 rounded-xl text-xs font-bold transition-all ${
              activeTab === "bundles"
                ? "bg-blue-600 text-white shadow"
                : "text-slate-400 hover:text-white hover:bg-slate-900"
            }`}
          >
            <GitMerge className="w-4 h-4" />
            <span>3. Auto-Shadow Bundling Gate</span>
          </button>

          <button
            onClick={() => setActiveTab("schedule")}
            className={`flex items-center space-x-2 py-2.5 px-4 rounded-xl text-xs font-bold transition-all ${
              activeTab === "schedule"
                ? "bg-blue-600 text-white shadow"
                : "text-slate-400 hover:text-white hover:bg-slate-900"
            }`}
          >
            <Calendar className="w-4 h-4" />
            <span>4. CP-SAT Weekly Block Plan</span>
          </button>
        </div>

        {/* Tab Views */}
        <div>
          {activeTab === "topology" && (
            <div className="space-y-6">
              <TopologyView
                tasks={tasks}
                onSelectTask={(t) => setSelectedTask(t)}
              />
              <TaskListView
                tasks={tasks}
                onSelectTask={(t) => setSelectedTask(t)}
              />
            </div>
          )}

          {activeTab === "tasks" && (
            <TaskListView
              tasks={tasks}
              onSelectTask={(t) => setSelectedTask(t)}
            />
          )}

          {activeTab === "bundles" && (
            <BundleView bundles={bundles} />
          )}

          {activeTab === "schedule" && (
            <ScheduleGanttView
              schedule={scheduleData.schedule || []}
              stats={scheduleData.stats || {}}
              onOfficerAction={(block) => setActionBlock(block)}
            />
          )}
        </div>
      </main>

      {/* Priority Breakdown Modal */}
      {selectedTask && (
        <PriorityBreakdownView
          task={selectedTask}
          policyMode={policyMode}
          onClose={() => setSelectedTask(null)}
        />
      )}

      {/* Officer Action Modal */}
      {actionBlock && (
        <OfficerActionModal
          block={actionBlock}
          onClose={() => setActionBlock(null)}
          onSubmit={handleOfficerSubmit}
        />
      )}

      {/* Canonical Contracts Modal */}
      {showContractsModal && (
        <CanonicalContractsModal onClose={() => setShowContractsModal(false)} />
      )}

      {/* Honesty Points & Q&A Modal */}
      {showQAModal && (
        <HonestyPointsModal onClose={() => setShowQAModal(false)} />
      )}
    </div>
  );
}
