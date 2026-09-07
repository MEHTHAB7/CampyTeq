import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
} from "react-native";
import { useAuth } from "../context/AuthContext";
import { mobileApiRequest } from "../services/api";
import {
  Clock,
  CheckCircle2,
  AlertTriangle,
  BookOpen,
  DollarSign,
  Printer,
  Sparkles,
  LogOut,
  ChevronRight,
  ShieldAlert,
} from "lucide-react-native";

export const DashboardScreen: React.FC<{ navigation: any }> = ({ navigation }) => {
  const { user, logout } = useAuth();
  const [refreshing, setRefreshing] = useState(false);
  const [timetableToday, setTimetableToday] = useState<any[]>([]);
  const [attendanceRate, setAttendanceRate] = useState<number>(85.0);
  const [riskData, setRiskData] = useState<any>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      // 1. Fetch Today's Timetable
      const tt = await mobileApiRequest<any>("/academics/timetable/today/");
      if (tt && Array.isArray(tt)) setTimetableToday(tt);

      // 2. Fetch confidential AI risk assessment for this student
      const ai = await mobileApiRequest<any>("/analytics/ai-risk/");
      const records = ai.results || ai.data || (Array.isArray(ai) ? ai : []);
      if (records.length > 0) {
        setRiskData(records[0]);
        setAttendanceRate(records[0].attendance_rate || 85.0);
      }
    } catch (err) {
      console.log("Error loading mobile dashboard data", err);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#818cf8" />}
    >
      {/* Student Welcome Card */}
      <View style={styles.welcomeCard}>
        <View style={styles.topRow}>
          <View>
            <Text style={styles.greeting}>Welcome back,</Text>
            <Text style={styles.userName}>{user?.first_name} {user?.last_name}</Text>
            <Text style={styles.userMeta}>
              {user?.college_name || "Apex Institute of Technology"}
            </Text>
          </View>
          <TouchableOpacity style={styles.logoutBtn} onPress={logout}>
            <LogOut size={18} color="#94a3b8" />
          </TouchableOpacity>
        </View>

        <View style={styles.profileChips}>
          <View style={styles.chip}>
            <Text style={styles.chipText}>Roll: {user?.roll_number || "2026-CSE-042"}</Text>
          </View>
          <View style={styles.chip}>
            <Text style={styles.chipText}>CSE • Sem 6</Text>
          </View>
        </View>
      </View>

      {/* KPI Stats Row */}
      <View style={styles.kpiRow}>
        <View style={styles.kpiBox}>
          <Text style={styles.kpiLabel}>Attendance</Text>
          <Text
            style={[
              styles.kpiValue,
              attendanceRate < 75 ? styles.dangerText : styles.successText,
            ]}
          >
            {attendanceRate}%
          </Text>
          <Text style={styles.kpiSub}>
            {attendanceRate < 75 ? "Defaulter Standing" : "Compliant (≥ 75%)"}
          </Text>
        </View>

        <View style={styles.kpiBox}>
          <Text style={styles.kpiLabel}>Risk Radar</Text>
          <Text
            style={[
              styles.kpiValue,
              riskData?.risk_level === "HIGH" || riskData?.risk_level === "CRITICAL"
                ? styles.dangerText
                : styles.warningText,
            ]}
          >
            {riskData?.risk_level || "LOW"}
          </Text>
          <Text style={styles.kpiSub}>Score: {riskData?.score || "12.0"}/100</Text>
        </View>
      </View>

      {/* AI Advisory Callout */}
      {riskData && (
        <TouchableOpacity
          style={[
            styles.aiAlertCard,
            riskData.risk_level === "HIGH" ? styles.aiCardWarning : styles.aiCardNormal,
          ]}
          onPress={() => navigation.navigate("AIRadar")}
        >
          <View style={styles.aiHeader}>
            <View style={styles.aiBadge}>
              <Sparkles size={14} color="#818cf8" />
              <Text style={styles.aiBadgeText}>AI Academic Guidance</Text>
            </View>
            <ChevronRight size={16} color="#94a3b8" />
          </View>
          <Text style={styles.aiSummary}>
            {riskData.key_risk_drivers?.[0] || "Academic trajectory is steady with active submissions."}
          </Text>
        </TouchableOpacity>
      )}

      {/* Today's Schedule Section */}
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>Today's Schedule</Text>
        <Text style={styles.sectionSubtitle}>
          {timetableToday.length} sessions scheduled
        </Text>
      </View>

      {timetableToday.length === 0 ? (
        <View style={styles.emptyCard}>
          <Clock size={28} color="#64748b" />
          <Text style={styles.emptyTitle}>No More Classes Today</Text>
          <Text style={styles.emptyDesc}>Enjoy your self-study time or lab project review.</Text>
        </View>
      ) : (
        timetableToday.map((slot: any, idx: number) => (
          <View key={idx} style={styles.slotCard}>
            <View style={styles.slotTimeCol}>
              <Text style={styles.slotStart}>{slot.start_time?.slice(0, 5)}</Text>
              <Text style={styles.slotEnd}>{slot.end_time?.slice(0, 5)}</Text>
            </View>
            <View style={styles.slotInfoCol}>
              <Text style={styles.slotSubject}>{slot.subject_name || slot.subject_code}</Text>
              <Text style={styles.slotFaculty}>{slot.faculty_name} • {slot.classroom_name || "Room 204"}</Text>
            </View>
          </View>
        ))
      )}

      {/* Quick Navigation Action Grid */}
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>Campus Quick Services</Text>
      </View>

      <View style={styles.actionGrid}>
        <TouchableOpacity
          style={styles.actionCard}
          onPress={() => navigation.navigate("Attendance")}
        >
          <View style={[styles.actionIcon, { backgroundColor: "#064e3b" }]}>
            <CheckCircle2 size={20} color="#34d399" />
          </View>
          <Text style={styles.actionTitle}>Attendance</Text>
          <Text style={styles.actionDesc}>Check subject percentages</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionCard}
          onPress={() => navigation.navigate("Assignments")}
        >
          <View style={[styles.actionIcon, { backgroundColor: "#1e1b4b" }]}>
            <BookOpen size={20} color="#818cf8" />
          </View>
          <Text style={styles.actionTitle}>Assignments</Text>
          <Text style={styles.actionDesc}>Active deadlines & marks</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionCard}
          onPress={() => navigation.navigate("Fees")}
        >
          <View style={[styles.actionIcon, { backgroundColor: "#065f46" }]}>
            <DollarSign size={20} color="#6ee7b7" />
          </View>
          <Text style={styles.actionTitle}>Fees & Dues</Text>
          <Text style={styles.actionDesc}>Invoices & instant pay</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionCard}
          onPress={() => navigation.navigate("PrintShop")}
        >
          <View style={[styles.actionIcon, { backgroundColor: "#451a03" }]}>
            <Printer size={20} color="#fbbf24" />
          </View>
          <Text style={styles.actionTitle}>Print Shop</Text>
          <Text style={styles.actionDesc}>Job queue & PIN pickup</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#020617",
  },
  content: {
    padding: 20,
    paddingBottom: 40,
  },
  welcomeCard: {
    backgroundColor: "#0f172a",
    borderColor: "#1e293b",
    borderWidth: 1,
    borderRadius: 20,
    padding: 20,
    marginBottom: 16,
  },
  topRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
  },
  greeting: {
    fontSize: 12,
    color: "#94a3b8",
    fontWeight: "500",
  },
  userName: {
    fontSize: 22,
    fontWeight: "bold",
    color: "#f8fafc",
    marginTop: 2,
  },
  userMeta: {
    fontSize: 12,
    color: "#818cf8",
    marginTop: 2,
  },
  logoutBtn: {
    padding: 8,
    borderRadius: 10,
    backgroundColor: "#1e293b",
  },
  profileChips: {
    flexDirection: "row",
    gap: 8,
    marginTop: 14,
  },
  chip: {
    backgroundColor: "#1e293b",
    paddingVertical: 4,
    paddingHorizontal: 10,
    borderRadius: 8,
  },
  chipText: {
    fontSize: 11,
    color: "#cbd5e1",
    fontWeight: "600",
  },
  kpiRow: {
    flexDirection: "row",
    gap: 12,
    marginBottom: 16,
  },
  kpiBox: {
    flex: 1,
    backgroundColor: "#0f172a",
    borderColor: "#1e293b",
    borderWidth: 1,
    borderRadius: 16,
    padding: 16,
  },
  kpiLabel: {
    fontSize: 11,
    color: "#94a3b8",
    fontWeight: "600",
    textTransform: "uppercase",
  },
  kpiValue: {
    fontSize: 26,
    fontWeight: "bold",
    marginTop: 4,
  },
  kpiSub: {
    fontSize: 10,
    color: "#64748b",
    marginTop: 2,
  },
  dangerText: {
    color: "#f87171",
  },
  successText: {
    color: "#34d399",
  },
  warningText: {
    color: "#fbbf24",
  },
  aiAlertCard: {
    borderRadius: 16,
    padding: 16,
    marginBottom: 20,
    borderWidth: 1,
  },
  aiCardNormal: {
    backgroundColor: "rgba(30, 27, 75, 0.4)",
    borderColor: "#4338ca",
  },
  aiCardWarning: {
    backgroundColor: "rgba(69, 26, 3, 0.4)",
    borderColor: "#b45309",
  },
  aiHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  aiBadge: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
  },
  aiBadgeText: {
    fontSize: 12,
    fontWeight: "700",
    color: "#c7d2fe",
  },
  aiSummary: {
    fontSize: 13,
    color: "#e2e8f0",
    lineHeight: 18,
  },
  sectionHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "baseline",
    marginBottom: 12,
    marginTop: 8,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#f8fafc",
  },
  sectionSubtitle: {
    fontSize: 12,
    color: "#64748b",
  },
  emptyCard: {
    backgroundColor: "#0f172a",
    borderColor: "#1e293b",
    borderWidth: 1,
    borderRadius: 16,
    padding: 24,
    alignItems: "center",
    marginBottom: 20,
  },
  emptyTitle: {
    fontSize: 14,
    fontWeight: "700",
    color: "#cbd5e1",
    marginTop: 10,
  },
  emptyDesc: {
    fontSize: 12,
    color: "#64748b",
    marginTop: 4,
    textAlign: "center",
  },
  slotCard: {
    flexDirection: "row",
    backgroundColor: "#0f172a",
    borderColor: "#1e293b",
    borderWidth: 1,
    borderRadius: 14,
    padding: 14,
    marginBottom: 10,
    alignItems: "center",
  },
  slotTimeCol: {
    paddingRight: 14,
    borderRightWidth: 1,
    borderColor: "#1e293b",
    alignItems: "center",
  },
  slotStart: {
    fontSize: 14,
    fontWeight: "bold",
    color: "#f8fafc",
  },
  slotEnd: {
    fontSize: 11,
    color: "#64748b",
  },
  slotInfoCol: {
    paddingLeft: 14,
    flex: 1,
  },
  slotSubject: {
    fontSize: 14,
    fontWeight: "bold",
    color: "#f8fafc",
  },
  slotFaculty: {
    fontSize: 12,
    color: "#94a3b8",
    marginTop: 2,
  },
  actionGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 12,
  },
  actionCard: {
    width: "48%",
    backgroundColor: "#0f172a",
    borderColor: "#1e293b",
    borderWidth: 1,
    borderRadius: 16,
    padding: 16,
  },
  actionIcon: {
    width: 40,
    height: 40,
    borderRadius: 12,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 10,
  },
  actionTitle: {
    fontSize: 14,
    fontWeight: "bold",
    color: "#f8fafc",
  },
  actionDesc: {
    fontSize: 11,
    color: "#64748b",
    marginTop: 2,
  },
});
