import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from "react-native";
import { Printer, Clock, CheckCircle2, ChevronLeft, Key, FileText } from "lucide-react-native";

export const PrintShopScreen: React.FC<{ navigation: any }> = ({ navigation }) => {
  const [orders, setOrders] = useState([
    {
      id: "PO-2026-0089",
      document_name: "Compiler_Design_Lab_Manual_Final.pdf",
      page_count: 14,
      total_cost: "28.00",
      color_mode: "B&W",
      binding_type: "SPIRAL",
      status: "READY_FOR_PICKUP",
      pickup_pin: "7482",
      created_at: "Today, 10:15 AM",
    },
    {
      id: "PO-2026-0072",
      document_name: "Algorithms_Term_Paper.pdf",
      page_count: 8,
      total_cost: "16.00",
      color_mode: "B&W",
      binding_type: "STAPLE",
      status: "COMPLETED",
      pickup_pin: "3910",
      created_at: "Yesterday, 03:40 PM",
    },
  ]);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Header */}
      <View style={styles.headerRow}>
        <TouchableOpacity style={styles.backBtn} onPress={() => navigation.goBack()}>
          <ChevronLeft size={20} color="#f8fafc" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Campus Print Shop</Text>
      </View>

      {/* Pricing info card */}
      <View style={styles.infoCard}>
        <Printer size={24} color="#fbbf24" />
        <View style={styles.infoTextCol}>
          <Text style={styles.infoTitle}>Campus Fast Print Kiosks</Text>
          <Text style={styles.infoSub}>
            Standard B&W: ₹2/page • Color: ₹10/page • Spiral: ₹25
          </Text>
        </View>
      </View>

      <Text style={styles.sectionTitle}>Your Print Queue</Text>

      {orders.map((order, idx) => {
        const isReady = order.status === "READY_FOR_PICKUP";
        return (
          <View key={idx} style={styles.orderCard}>
            <View style={styles.orderTop}>
              <Text style={styles.orderId}>{order.id}</Text>
              {isReady ? (
                <View style={styles.badgeReady}>
                  <Text style={styles.badgeTextReady}>READY FOR PICKUP</Text>
                </View>
              ) : (
                <View style={styles.badgeDone}>
                  <Text style={styles.badgeTextDone}>DELIVERED / ARCHIVED</Text>
                </View>
              )}
            </View>

            <View style={styles.docRow}>
              <FileText size={16} color="#818cf8" />
              <Text style={styles.docName} numberOfLines={1}>
                {order.document_name}
              </Text>
            </View>

            <View style={styles.specRow}>
              <Text style={styles.specText}>
                {order.page_count} Pages • {order.color_mode} • {order.binding_type}
              </Text>
              <Text style={styles.costText}>₹{order.total_cost}</Text>
            </View>

            {isReady && (
              <View style={styles.pinBox}>
                <View style={styles.pinLeft}>
                  <Key size={16} color="#fbbf24" />
                  <Text style={styles.pinLabel}>Kiosk Pickup PIN:</Text>
                </View>
                <Text style={styles.pinValue}>{order.pickup_pin}</Text>
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
  infoCard: {
    backgroundColor: "rgba(69, 26, 3, 0.3)",
    borderColor: "#b45309",
    borderWidth: 1,
    borderRadius: 16,
    padding: 16,
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    marginBottom: 20,
  },
  infoTextCol: {
    flex: 1,
  },
  infoTitle: {
    fontSize: 13,
    fontWeight: "bold",
    color: "#fde68a",
  },
  infoSub: {
    fontSize: 11,
    color: "#fef3c7",
    marginTop: 2,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#f8fafc",
    marginBottom: 12,
  },
  orderCard: {
    backgroundColor: "#0f172a",
    borderColor: "#1e293b",
    borderWidth: 1,
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
  },
  orderTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 10,
  },
  orderId: {
    fontSize: 11,
    color: "#818cf8",
    fontWeight: "700",
  },
  badgeReady: {
    backgroundColor: "rgba(16, 185, 129, 0.2)",
    paddingVertical: 3,
    paddingHorizontal: 8,
    borderRadius: 8,
  },
  badgeTextReady: {
    fontSize: 10,
    color: "#34d399",
    fontWeight: "700",
  },
  badgeDone: {
    backgroundColor: "rgba(100, 116, 139, 0.2)",
    paddingVertical: 3,
    paddingHorizontal: 8,
    borderRadius: 8,
  },
  badgeTextDone: {
    fontSize: 10,
    color: "#94a3b8",
    fontWeight: "600",
  },
  docRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginBottom: 10,
  },
  docName: {
    fontSize: 14,
    fontWeight: "bold",
    color: "#f8fafc",
    flex: 1,
  },
  specRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 10,
  },
  specText: {
    fontSize: 11,
    color: "#64748b",
  },
  costText: {
    fontSize: 14,
    fontWeight: "bold",
    color: "#f8fafc",
  },
  pinBox: {
    backgroundColor: "#020617",
    borderColor: "#334155",
    borderWidth: 1,
    borderRadius: 12,
    padding: 12,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  pinLeft: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  pinLabel: {
    fontSize: 12,
    color: "#cbd5e1",
    fontWeight: "600",
  },
  pinValue: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#fbbf24",
    letterSpacing: 3,
  },
});
