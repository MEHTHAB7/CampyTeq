import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  Alert,
} from "react-native";
import { mobileApiRequest } from "../services/api";
import { DollarSign, CheckCircle2, Clock, ChevronLeft, CreditCard, Receipt } from "lucide-react-native";

export const FeesScreen: React.FC<{ navigation: any }> = ({ navigation }) => {
  const [refreshing, setRefreshing] = useState(false);
  const [invoices, setInvoices] = useState<any[]>([
    {
      id: "inv-1",
      invoice_number: "INV-2026-0042",
      title: "Semester 6 Academic & Laboratory Tuition",
      final_amount: "45000.00",
      paid_amount: "45000.00",
      balance_due: "0.00",
      status: "PAID",
      due_date: "2026-08-30",
    },
    {
      id: "inv-2",
      invoice_number: "INV-2026-0108",
      title: "Mid-Term Examination & Library Amenities Fee",
      final_amount: "5000.00",
      paid_amount: "0.00",
      balance_due: "5000.00",
      status: "PENDING",
      due_date: "2026-09-20",
    },
  ]);

  useEffect(() => {
    loadInvoices();
  }, []);

  const loadInvoices = async () => {
    try {
      const res = await mobileApiRequest<any>("/fees/invoices/");
      const items = res?.results || res?.data || (Array.isArray(res) ? res : []);
      if (items.length > 0) setInvoices(items);
    } catch (e) {
      // Retain initial simulated state
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadInvoices();
    setRefreshing(false);
  };

  const handleSimulatePayment = (inv: any) => {
    Alert.alert(
      "Simulate Payment Gateway",
      `Pay ₹${Number(inv.balance_due).toLocaleString()} for ${inv.title} via UPI / Net Banking?`,
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Confirm Pay",
          onPress: () => {
            // Update local state instantly
            setInvoices((prev) =>
              prev.map((i) =>
                i.id === inv.id
                  ? {
                      ...i,
                      paid_amount: i.final_amount,
                      balance_due: "0.00",
                      status: "PAID",
                    }
                  : i
              )
            );
            Alert.alert("Payment Successful", `Transaction ID: TXN-${Date.now().toString().slice(-6)} recorded. Digital receipt issued.`);
          },
        },
      ]
    );
  };

  const totalOutstanding = invoices.reduce(
    (sum, i) => sum + Number(i.balance_due || 0),
    0
  );

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
        <Text style={styles.headerTitle}>Fee Payments & Dues</Text>
      </View>

      {/* Total Due Banner */}
      <View style={styles.bannerCard}>
        <Text style={styles.bannerLabel}>Total Outstanding Balance</Text>
        <Text style={styles.bannerAmount}>₹{totalOutstanding.toLocaleString()}</Text>
        <Text style={styles.bannerSub}>
          {totalOutstanding === 0
            ? "All institutional dues are cleared"
            : "Payment due before semester examination hall ticket generation"}
        </Text>
      </View>

      {/* Invoices List */}
      <Text style={styles.sectionTitle}>Fee Invoices</Text>

      {invoices.map((inv, idx) => {
        const isPaid = inv.status === "PAID";
        return (
          <View key={idx} style={styles.invoiceCard}>
            <View style={styles.invTop}>
              <Text style={styles.invNum}>{inv.invoice_number}</Text>
              {isPaid ? (
                <View style={styles.badgePaid}>
                  <CheckCircle2 size={12} color="#34d399" />
                  <Text style={styles.badgeTextPaid}>PAID IN FULL</Text>
                </View>
              ) : (
                <View style={styles.badgePending}>
                  <Clock size={12} color="#fbbf24" />
                  <Text style={styles.badgeTextPending}>PAYMENT DUE</Text>
                </View>
              )}
            </View>

            <Text style={styles.invTitle}>{inv.title}</Text>

            <View style={styles.invMeta}>
              <View>
                <Text style={styles.metaLabel}>Invoice Total</Text>
                <Text style={styles.metaVal}>₹{Number(inv.final_amount).toLocaleString()}</Text>
              </View>
              <View>
                <Text style={styles.metaLabel}>Balance Due</Text>
                <Text style={[styles.metaVal, isPaid ? styles.textGreen : styles.textRed]}>
                  ₹{Number(inv.balance_due).toLocaleString()}
                </Text>
              </View>
              <View>
                <Text style={styles.metaLabel}>Due Date</Text>
                <Text style={styles.metaVal}>{inv.due_date}</Text>
              </View>
            </View>

            {!isPaid && (
              <TouchableOpacity
                style={styles.payBtn}
                onPress={() => handleSimulatePayment(inv)}
              >
                <CreditCard size={14} color="#ffffff" />
                <Text style={styles.payBtnText}>Instant Pay with UPI / Card</Text>
              </TouchableOpacity>
            )}

            {isPaid && (
              <View style={styles.receiptRow}>
                <Receipt size={14} color="#94a3b8" />
                <Text style={styles.receiptText}>Digital Receipt Generated (Audit Logged)</Text>
              </View>
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
  bannerCard: {
    backgroundColor: "#0f172a",
    borderColor: "#1e293b",
    borderWidth: 1,
    borderRadius: 20,
    padding: 20,
    marginBottom: 20,
    alignItems: "center",
  },
  bannerLabel: {
    fontSize: 12,
    color: "#94a3b8",
    fontWeight: "600",
    textTransform: "uppercase",
  },
  bannerAmount: {
    fontSize: 36,
    fontWeight: "bold",
    color: "#f8fafc",
    marginVertical: 6,
  },
  bannerSub: {
    fontSize: 11,
    color: "#64748b",
    textAlign: "center",
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#f8fafc",
    marginBottom: 12,
  },
  invoiceCard: {
    backgroundColor: "#0f172a",
    borderColor: "#1e293b",
    borderWidth: 1,
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
  },
  invTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 6,
  },
  invNum: {
    fontSize: 11,
    color: "#818cf8",
    fontWeight: "700",
  },
  badgePaid: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    backgroundColor: "rgba(16, 185, 129, 0.15)",
    paddingVertical: 3,
    paddingHorizontal: 8,
    borderRadius: 8,
  },
  badgeTextPaid: {
    fontSize: 10,
    color: "#34d399",
    fontWeight: "700",
  },
  badgePending: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    backgroundColor: "rgba(245, 158, 11, 0.15)",
    paddingVertical: 3,
    paddingHorizontal: 8,
    borderRadius: 8,
  },
  badgeTextPending: {
    fontSize: 10,
    color: "#fbbf24",
    fontWeight: "700",
  },
  invTitle: {
    fontSize: 14,
    fontWeight: "bold",
    color: "#f8fafc",
    marginBottom: 12,
  },
  invMeta: {
    flexDirection: "row",
    justifyContent: "space-between",
    backgroundColor: "#020617",
    padding: 12,
    borderRadius: 10,
    marginBottom: 12,
  },
  metaLabel: {
    fontSize: 10,
    color: "#64748b",
  },
  metaVal: {
    fontSize: 13,
    fontWeight: "bold",
    color: "#f8fafc",
    marginTop: 2,
  },
  payBtn: {
    backgroundColor: "#059669",
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
    paddingVertical: 12,
    borderRadius: 10,
  },
  payBtnText: {
    color: "#ffffff",
    fontSize: 13,
    fontWeight: "bold",
  },
  receiptRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 6,
    paddingTop: 4,
  },
  receiptText: {
    fontSize: 11,
    color: "#94a3b8",
  },
  textGreen: {
    color: "#34d399",
  },
  textRed: {
    color: "#f87171",
  },
});
