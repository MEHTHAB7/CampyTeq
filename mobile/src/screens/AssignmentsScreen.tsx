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
import { BookOpen, Clock, CheckCircle2, ChevronLeft, Calendar } from "lucide-react-native";

export const AssignmentsScreen: React.FC<{ navigation: any }> = ({ navigation }) => {
  const [refreshing, setRefreshing] = useState(false);
  const [assignments, setAssignments] = useState<any[]>([
    {
      id: "1",
      title: "AVL Tree & B-Tree Balancing Simulator",
      subject: "CS301: Data Structures",
      due_date: "2026-09-15",
      maximum_marks: "100.00",
      status: "ACTIVE",
      submission_status: "PENDING",
    },
    {
      id: "2",
      title: "Query Optimization & ACID Benchmarking",
      subject: "CS302: DBMS",
      due_date: "2026-09-12",
      maximum_marks: "50.00",
      status: "ACTIVE",
      submission_status: "SUBMITTED",
      marks_awarded: "46.00",
    },
    {
      id: "3",
      title: "POSIX Threads & Deadlock Detection",
      subject: "CS303: Operating Systems",
      due_date: "2026-09-08",
      maximum_marks: "50.00",
      status: "ACTIVE",
      submission_status: "PENDING",
    },
  ]);

  useEffect(() => {
    loadAssignments();
  }, []);

  const loadAssignments = async () => {
    try {
      const res = await mobileApiRequest<any>("/assignments/assignments/");
      const items = res?.results || res?.data || (Array.isArray(res) ? res : []);
      if (items.length > 0) {
        setAssignments(items);
      }
    } catch (e) {
      // Keep initial demo state
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadAssignments();
    setRefreshing(false);
  };

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#818cf8" />}
    >
      {/* Header with back button */}
      <View style={styles.headerRow}>
        <TouchableOpacity style={styles.backBtn} onPress={() => navigation.goBack()}>
          <ChevronLeft size={20} color="#f8fafc" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Assignments & Tasks</Text>
      </View>

      <Text style={styles.sectionTitle}>Course Assignments</Text>

      {assignments.map((item, idx) => {
        const isSubmitted = item.submission_status === "SUBMITTED";
        return (
          <View key={idx} style={styles.card}>
            <View style={styles.cardHeader}>
              <Text style={styles.subjectCode}>{item.subject}</Text>
              {isSubmitted ? (
                <View style={styles.statusBadgeGreen}>
                  <CheckCircle2 size={12} color="#34d399" />
                  <Text style={styles.statusTextGreen}>Submitted</Text>
                </View>
              ) : (
                <View style={styles.statusBadgeAmber}>
                  <Clock size={12} color="#fbbf24" />
                  <Text style={styles.statusTextAmber}>Pending</Text>
                </View>
              )}
            </View>

            <Text style={styles.title}>{item.title}</Text>

            <View style={styles.metaRow}>
              <View style={styles.metaItem}>
                <Calendar size={12} color="#94a3b8" />
                <Text style={styles.metaText}>Due: {item.due_date}</Text>
              </View>
              <Text style={styles.maxMarks}>Max: {Math.round(Number(item.maximum_marks))} pts</Text>
            </View>

            {item.marks_awarded && (
              <View style={styles.gradeBox}>
                <Text style={styles.gradeLabel}>Evaluation Score:</Text>
                <Text style={styles.gradeScore}>
                  {item.marks_awarded} / {Math.round(Number(item.maximum_marks))}
                </Text>
              </View>
            )}

            {!isSubmitted && (
              <TouchableOpacity style={styles.submitBtn}>
                <Text style={styles.submitBtnText}>Submit Assignment Document</Text>
              </TouchableOpacity>
            )}
          </View>
        );
      })}
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
  sectionTitle: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#f8fafc",
    marginBottom: 12,
  },
  card: {
    backgroundColor: "#0f172a",
    borderColor: "#1e293b",
    borderWidth: 1,
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
  },
  cardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  subjectCode: {
    fontSize: 11,
    color: "#818cf8",
    fontWeight: "700",
  },
  statusBadgeGreen: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    backgroundColor: "rgba(16, 185, 129, 0.15)",
    paddingVertical: 3,
    paddingHorizontal: 8,
    borderRadius: 10,
  },
  statusTextGreen: {
    fontSize: 10,
    color: "#34d399",
    fontWeight: "700",
  },
  statusBadgeAmber: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    backgroundColor: "rgba(245, 158, 11, 0.15)",
    paddingVertical: 3,
    paddingHorizontal: 8,
    borderRadius: 10,
  },
  statusTextAmber: {
    fontSize: 10,
    color: "#fbbf24",
    fontWeight: "700",
  },
  title: {
    fontSize: 14,
    fontWeight: "bold",
    color: "#f8fafc",
    marginBottom: 10,
    lineHeight: 20,
  },
  metaRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingTop: 8,
    borderTopWidth: 1,
    borderColor: "#1e293b",
  },
  metaItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
  },
  metaText: {
    fontSize: 11,
    color: "#94a3b8",
  },
  maxMarks: {
    fontSize: 11,
    color: "#cbd5e1",
    fontWeight: "600",
  },
  gradeBox: {
    marginTop: 10,
    backgroundColor: "#020617",
    padding: 10,
    borderRadius: 10,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  gradeLabel: {
    fontSize: 11,
    color: "#94a3b8",
  },
  gradeScore: {
    fontSize: 13,
    fontWeight: "bold",
    color: "#34d399",
  },
  submitBtn: {
    marginTop: 12,
    backgroundColor: "#4f46e5",
    paddingVertical: 10,
    borderRadius: 10,
    alignItems: "center",
  },
  submitBtnText: {
    fontSize: 12,
    fontWeight: "bold",
    color: "#ffffff",
  },
});
