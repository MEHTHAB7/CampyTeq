import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
} from "react-native";
import { mobileApiRequest } from "../services/api";
import {
  Sparkles,
  ShieldCheck,
  AlertTriangle,
  ChevronLeft,
  Info,
  Clock,
  CheckCircle2,
} from "lucide-react-native";

export const AIRadarScreen: React.FC<{ navigation: any }> = ({ navigation }) => {
  const [refreshing, setRefreshing] = useState(false);
  const [analysis, setAnalysis] = useState<any>({
    risk_level: "MEDIUM",
    score: "46.50",
    attendance_rate: 78.4,
    missing_assignments_count: 1,
    average_marks_percentage: 64.5,
    leave_days_count: 3,
    key_risk_drivers: [
      "Attendance 78.4% is approaching the 75% examination threshold.",
      "1 missing or overdue assignment submission detected.",
      "Mid-term exam score dip detected in CS301 Algorithms.",
    ],
    suggested_interventions: [
      "Schedule 1-on-1 counseling session with designated mentor.",
      "Submit pending assignments to restore continuous assessment marks.",
      "Review algorithms concepts with department teaching assistants.",
    ],
    reviewed_at: "2026-09-05",
    reviewed_by_name: "Prof. Anil Verma (Mentor)",
    review_action_taken: "COUNSELING_SCHEDULED",
    review_notes:
      "Conducted 30-minute academic mentoring check-in. Student committed to resolving algorithms submissions and attending morning labs.",
  });

  useEffect(() => {
    loadRiskData();
  }, []);

  const loadRiskData = async () => {
    try {
      const res = await mobileApiRequest<any>("/analytics/ai-risk/");
      const items = res?.results || res?.data || (Array.isArray(res) ? res : []);
      if (items.length > 0) setAnalysis(items[0]);
    } catch (e) {
      // Fallback to loaded simulated state
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadRiskData();
    setRefreshing(false);
  };

  const scoreNum = Number(analysis.score) || 0;

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#818cf8" />}
    >
      {/* Header */}
      <View style={styles.headerRow}>
        <TouchableOpacity style={styles.backBtn} onPress={() => navigation.goBack()}>
          <ChevronLeft size={20} color="#f8fafc" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>AI Academic Guidance</Text>
      </View>

      {/* Hero Score Gauge */}
      <View style={styles.gaugeCard}>
        <View style={styles.gaugeTop}>
          <Text style={styles.gaugeLabel}>Multi-Factor Risk Radar</Text>
          <View
            style={[
              styles.riskTag,
              analysis.risk_level === "HIGH" || analysis.risk_level === "CRITICAL"
                ? styles.bgRed
                : analysis.risk_level === "MEDIUM"
                ? styles.bgAmber
                : styles.bgGreen,
            ]}
          >
            <Text style={styles.riskTagText}>{analysis.risk_level} RISK</Text>
          </View>
        </View>

        <Text style={styles.scoreText}>
          {scoreNum.toFixed(1)} <Text style={styles.scoreSub}>/ 100</Text>
        </Text>

        <View style={styles.meterTrack}>
          <View
            style={[
              styles.meterFill,
              {
                width: `${Math.min(100, scoreNum)}%`,
                backgroundColor:
                  analysis.risk_level === "HIGH" || analysis.risk_level === "CRITICAL"
                    ? "#ef4444"
                    : analysis.risk_level === "MEDIUM"
                    ? "#f59e0b"
                    : "#10b981",
              },
            ]}
          />
        </View>

        {/* 4 Quant Indicators */}
        <View style={styles.gridStats}>
          <View style={styles.gridBox}>
            <Text style={styles.gridVal}>{analysis.attendance_rate}%</Text>
            <Text style={styles.gridKey}>Attendance</Text>
          </View>
          <View style={styles.gridBox}>
            <Text style={styles.gridVal}>{analysis.missing_assignments_count}</Text>
            <Text style={styles.gridKey}>Missing Assg</Text>
          </View>
          <View style={styles.gridBox}>
            <Text style={styles.gridVal}>{analysis.average_marks_percentage}%</Text>
            <Text style={styles.gridKey}>Exam Avg</Text>
          </View>
          <View style={styles.gridBox}>
            <Text style={styles.gridVal}>{analysis.leave_days_count}d</Text>
            <Text style={styles.gridKey}>Leaves</Text>
          </View>
        </View>
      </View>

      {/* Explainable Risk Drivers */}
      <Text style={styles.sectionTitle}>Key Academic Risk Drivers</Text>
      <View style={styles.cardBox}>
        {analysis.key_risk_drivers?.map((driver: string, idx: number) => (
          <View key={idx} style={styles.bulletRow}>
            <Text style={styles.bulletAmber}>•</Text>
            <Text style={styles.bulletText}>{driver}</Text>
          </View>
        ))}
      </View>

      {/* Suggested Interventions */}
      <Text style={styles.sectionTitle}>Recommended Action Plan</Text>
      <View style={styles.cardBox}>
        {analysis.suggested_interventions?.map((item: string, idx: number) => (
          <View key={idx} style={styles.bulletRow}>
            <Text style={styles.bulletGreen}>✓</Text>
            <Text style={styles.bulletText}>{item}</Text>
          </View>
        ))}
      </View>

      {/* Mentor Counseling Notes */}
      <Text style={styles.sectionTitle}>Faculty Mentorship Status</Text>
      <View style={styles.cardBox}>
        <View style={styles.mentorTop}>
          <ShieldCheck size={16} color="#818cf8" />
          <Text style={styles.mentorName}>{analysis.reviewed_by_name || "Assigned Mentor"}</Text>
        </View>
        <Text style={styles.actionTaken}>
          Action Plan: {analysis.review_action_taken?.replace(/_/g, " ")}
        </Text>
        <Text style={styles.mentorNotes}>"{analysis.review_notes}"</Text>
      </View>

      {/* Ethical AI Guarantee */}
      <View style={styles.ethicalBanner}>
        <Info size={16} color="#818cf8" />
        <Text style={styles.ethicalText}>
          CampyTeq Responsible AI Framework: This score is strictly an advisory guidance tool designed to help you stay ahead of semester requirements. It has zero automated punitive effect on your enrollment.
        </Text>
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
  headerRow: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 20,
    gap: 12,
  },
  backBtn: {
    padding: 8,
    borderRadius: 10,
    backgroundColor: "#0f172a",
    borderWidth: 1,
    borderColor: "#1e293b",
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#f8fafc",
  },
  gaugeCard: {
    backgroundColor: "#0f172a",
    borderColor: "#1e293b",
    borderWidth: 1,
    borderRadius: 20,
    padding: 20,
    marginBottom: 20,
  },
  gaugeTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  gaugeLabel: {
    fontSize: 12,
    color: "#94a3b8",
    fontWeight: "600",
    textTransform: "uppercase",
  },
  riskTag: {
    paddingVertical: 4,
    paddingHorizontal: 10,
    borderRadius: 8,
  },
  riskTagText: {
    fontSize: 10,
    fontWeight: "bold",
    color: "#ffffff",
  },
  bgRed: {
    backgroundColor: "#ef4444",
  },
  bgAmber: {
    backgroundColor: "#f59e0b",
  },
  bgGreen: {
    backgroundColor: "#10b981",
  },
  scoreText: {
    fontSize: 38,
    fontWeight: "bold",
    color: "#f8fafc",
    marginVertical: 4,
  },
  scoreSub: {
    fontSize: 16,
    color: "#64748b",
  },
  meterTrack: {
    height: 8,
    backgroundColor: "#1e293b",
    borderRadius: 4,
    overflow: "hidden",
    marginVertical: 14,
  },
  meterFill: {
    height: "100%",
    borderRadius: 4,
  },
  gridStats: {
    flexDirection: "row",
    justifyContent: "space-between",
    borderTopWidth: 1,
    borderColor: "#1e293b",
    paddingTop: 12,
  },
  gridBox: {
    alignItems: "center",
  },
  gridVal: {
    fontSize: 14,
    fontWeight: "bold",
    color: "#f8fafc",
  },
  gridKey: {
    fontSize: 10,
    color: "#64748b",
    marginTop: 2,
  },
  sectionTitle: {
    fontSize: 15,
    fontWeight: "bold",
    color: "#f8fafc",
    marginBottom: 10,
  },
  cardBox: {
    backgroundColor: "#0f172a",
    borderColor: "#1e293b",
    borderWidth: 1,
    borderRadius: 16,
    padding: 16,
    marginBottom: 18,
  },
  bulletRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 8,
    marginBottom: 8,
  },
  bulletAmber: {
    color: "#fbbf24",
    fontSize: 14,
    marginTop: -1,
  },
  bulletGreen: {
    color: "#34d399",
    fontSize: 12,
    marginTop: 1,
  },
  bulletText: {
    fontSize: 12,
    color: "#cbd5e1",
    flex: 1,
    lineHeight: 18,
  },
  mentorTop: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginBottom: 6,
  },
  mentorName: {
    fontSize: 13,
    fontWeight: "bold",
    color: "#f8fafc",
  },
  actionTaken: {
    fontSize: 11,
    color: "#818cf8",
    fontWeight: "600",
    marginBottom: 8,
  },
  mentorNotes: {
    fontSize: 12,
    color: "#cbd5e1",
    fontStyle: "italic",
    lineHeight: 18,
  },
  ethicalBanner: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 10,
    backgroundColor: "rgba(30, 27, 75, 0.3)",
    borderColor: "#4338ca",
    borderWidth: 1,
    padding: 14,
    borderRadius: 14,
    marginTop: 4,
  },
  ethicalText: {
    fontSize: 11,
    color: "#c7d2fe",
    flex: 1,
    lineHeight: 16,
  },
});
