import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from "react-native";
import { useAuth } from "../context/AuthContext";
import { ShieldCheck, GraduationCap, Sparkles } from "lucide-react-native";

export const LoginScreen: React.FC = () => {
  const { login, loginAsDemoStudent, isLoading } = useAuth();
  const [email, setEmail] = useState("student.rahul@apex.edu");
  const [password, setPassword] = useState("Password123!");
  const [error, setError] = useState<string | null>(null);

  const handleManualLogin = async () => {
    setError(null);
    try {
      await login(email, password);
    } catch (err: any) {
      setError(err.message || "Login failed. Please verify credentials.");
    }
  };

  const handleDemoSelect = async (type: "rahul" | "rohan" | "ananya") => {
    setError(null);
    try {
      await loginAsDemoStudent(type);
    } catch (err: any) {
      setError(err.message || "Demo login failed.");
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Brand Header */}
        <View style={styles.brandContainer}>
          <View style={styles.iconCircle}>
            <GraduationCap size={36} color="#818cf8" />
          </View>
          <Text style={styles.brandTitle}>CampyTeq</Text>
          <Text style={styles.brandSubtitle}>Student Mobile Portal</Text>
          <View style={styles.badge}>
            <Sparkles size={12} color="#38bdf8" />
            <Text style={styles.badgeText}>Connected Digital Campus</Text>
          </View>
        </View>

        {error && (
          <View style={styles.errorBox}>
            <Text style={styles.errorText}>{error}</Text>
          </View>
        )}

        {/* Input Form */}
        <View style={styles.formContainer}>
          <Text style={styles.inputLabel}>Institutional Email / Roll Number</Text>
          <TextInput
            style={styles.input}
            placeholder="student@apex.edu"
            placeholderTextColor="#64748b"
            value={email}
            onChangeText={setEmail}
            autoCapitalize="none"
            keyboardType="email-address"
          />

          <Text style={styles.inputLabel}>Password</Text>
          <TextInput
            style={styles.input}
            placeholder="••••••••••••"
            placeholderTextColor="#64748b"
            value={password}
            onChangeText={setPassword}
            secureTextEntry
          />

          <TouchableOpacity
            style={[styles.primaryButton, isLoading && styles.disabledButton]}
            onPress={handleManualLogin}
            disabled={isLoading}
          >
            {isLoading ? (
              <ActivityIndicator color="#ffffff" />
            ) : (
              <Text style={styles.primaryButtonText}>Sign In to Campus</Text>
            )}
          </TouchableOpacity>
        </View>

        {/* Quick Demo Student Switcher */}
        <View style={styles.demoSection}>
          <Text style={styles.demoHeading}>Instant Demo Profiles</Text>
          <View style={styles.demoRow}>
            <TouchableOpacity
              style={styles.demoChip}
              onPress={() => handleDemoSelect("rahul")}
              disabled={isLoading}
            >
              <Text style={styles.demoName}>Rahul Kumar</Text>
              <Text style={styles.demoRole}>B.Tech CSE • Med Risk</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.demoChip, styles.warningChip]}
              onPress={() => handleDemoSelect("rohan")}
              disabled={isLoading}
            >
              <Text style={styles.demoName}>Rohan Gupta</Text>
              <Text style={styles.demoRole}>Defaulter • High Risk</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.demoChip, styles.successChip]}
              onPress={() => handleDemoSelect("ananya")}
              disabled={isLoading}
            >
              <Text style={styles.demoName}>Ananya Sen</Text>
              <Text style={styles.demoRole}>Top Honors • Low Risk</Text>
            </TouchableOpacity>
          </View>
        </View>

        <View style={styles.privacyGuarantee}>
          <ShieldCheck size={14} color="#34d399" />
          <Text style={styles.privacyText}>
            Privacy Guaranteed: Zero continuous GPS tracking.
          </Text>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#020617",
  },
  scrollContent: {
    padding: 24,
    justifyContent: "center",
    minHeight: "100%",
  },
  brandContainer: {
    alignItems: "center",
    marginBottom: 32,
  },
  iconCircle: {
    width: 68,
    height: 68,
    borderRadius: 20,
    backgroundColor: "#1e1b4b",
    borderWidth: 1,
    borderColor: "#4338ca",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 12,
  },
  brandTitle: {
    fontSize: 28,
    fontWeight: "bold",
    color: "#f8fafc",
    letterSpacing: -0.5,
  },
  brandSubtitle: {
    fontSize: 14,
    color: "#94a3b8",
    marginTop: 4,
  },
  badge: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 20,
    backgroundColor: "#0f172a",
    borderColor: "#1e293b",
    borderWidth: 1,
    marginTop: 10,
  },
  badgeText: {
    fontSize: 11,
    color: "#38bdf8",
    fontWeight: "600",
  },
  errorBox: {
    backgroundColor: "rgba(239, 68, 68, 0.15)",
    borderColor: "#ef4444",
    borderWidth: 1,
    padding: 12,
    borderRadius: 12,
    marginBottom: 20,
  },
  errorText: {
    color: "#fca5a5",
    fontSize: 13,
    textAlign: "center",
  },
  formContainer: {
    backgroundColor: "rgba(15, 23, 42, 0.7)",
    borderColor: "#1e293b",
    borderWidth: 1,
    borderRadius: 20,
    padding: 20,
    marginBottom: 24,
  },
  inputLabel: {
    fontSize: 12,
    color: "#cbd5e1",
    fontWeight: "600",
    marginBottom: 8,
    textTransform: "uppercase",
    letterSpacing: 0.5,
  },
  input: {
    backgroundColor: "#020617",
    borderColor: "#334155",
    borderWidth: 1,
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    color: "#ffffff",
    fontSize: 15,
    marginBottom: 16,
  },
  primaryButton: {
    backgroundColor: "#4f46e5",
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 4,
  },
  disabledButton: {
    opacity: 0.6,
  },
  primaryButtonText: {
    color: "#ffffff",
    fontSize: 15,
    fontWeight: "700",
  },
  demoSection: {
    alignItems: "center",
    marginBottom: 24,
  },
  demoHeading: {
    fontSize: 12,
    color: "#64748b",
    fontWeight: "600",
    textTransform: "uppercase",
    letterSpacing: 1,
    marginBottom: 12,
  },
  demoRow: {
    flexDirection: "row",
    gap: 8,
    width: "100%",
    justifyContent: "space-between",
  },
  demoChip: {
    flex: 1,
    backgroundColor: "#0f172a",
    borderColor: "#312e81",
    borderWidth: 1,
    paddingVertical: 10,
    paddingHorizontal: 8,
    borderRadius: 12,
    alignItems: "center",
  },
  warningChip: {
    borderColor: "#854d0e",
  },
  successChip: {
    borderColor: "#065f46",
  },
  demoName: {
    fontSize: 12,
    fontWeight: "700",
    color: "#f8fafc",
  },
  demoRole: {
    fontSize: 9,
    color: "#94a3b8",
    marginTop: 2,
    textAlign: "center",
  },
  privacyGuarantee: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 6,
  },
  privacyText: {
    fontSize: 11,
    color: "#64748b",
  },
});
