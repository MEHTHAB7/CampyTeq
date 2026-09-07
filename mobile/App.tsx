import React, { useState } from "react";
import { StatusBar } from "expo-status-bar";
import { SafeAreaProvider, SafeAreaView } from "react-native-safe-area-context";
import { View, StyleSheet, TouchableOpacity, Text } from "react-native";
import { AuthProvider, useAuth } from "./src/context/AuthContext";
import { LoginScreen } from "./src/screens/LoginScreen";
import { DashboardScreen } from "./src/screens/DashboardScreen";
import { AttendanceScreen } from "./src/screens/AttendanceScreen";
import { AssignmentsScreen } from "./src/screens/AssignmentsScreen";
import { FeesScreen } from "./src/screens/FeesScreen";
import { PrintShopScreen } from "./src/screens/PrintShopScreen";
import { AIRadarScreen } from "./src/screens/AIRadarScreen";
import {
  Home,
  Clock,
  BookOpen,
  DollarSign,
  Printer,
  BrainCircuit,
} from "lucide-react-native";

type ScreenName = "Dashboard" | "Attendance" | "Assignments" | "Fees" | "PrintShop" | "AIRadar";

const MainNavigator: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const [currentScreen, setCurrentScreen] = useState<ScreenName>("Dashboard");

  if (!isAuthenticated) {
    return <LoginScreen />;
  }

  const navigation = {
    navigate: (name: ScreenName) => setCurrentScreen(name),
    goBack: () => setCurrentScreen("Dashboard"),
  };

  const renderScreen = () => {
    switch (currentScreen) {
      case "Attendance":
        return <AttendanceScreen navigation={navigation} />;
      case "Assignments":
        return <AssignmentsScreen navigation={navigation} />;
      case "Fees":
        return <FeesScreen navigation={navigation} />;
      case "PrintShop":
        return <PrintShopScreen navigation={navigation} />;
      case "AIRadar":
        return <AIRadarScreen navigation={navigation} />;
      case "Dashboard":
      default:
        return <DashboardScreen navigation={navigation} />;
    }
  };

  return (
    <SafeAreaView style={styles.safeArea} edges={["top", "bottom"]}>
      <StatusBar style="light" />
      <View style={styles.screenContainer}>{renderScreen()}</View>

      {/* Bottom Tab Bar */}
      <View style={styles.tabBar}>
        <TouchableOpacity
          style={styles.tabItem}
          onPress={() => setCurrentScreen("Dashboard")}
        >
          <Home
            size={20}
            color={currentScreen === "Dashboard" ? "#818cf8" : "#64748b"}
          />
          <Text
            style={[
              styles.tabLabel,
              currentScreen === "Dashboard" && styles.tabLabelActive,
            ]}
          >
            Home
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.tabItem}
          onPress={() => setCurrentScreen("Attendance")}
        >
          <Clock
            size={20}
            color={currentScreen === "Attendance" ? "#818cf8" : "#64748b"}
          />
          <Text
            style={[
              styles.tabLabel,
              currentScreen === "Attendance" && styles.tabLabelActive,
            ]}
          >
            Attend
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.tabItem}
          onPress={() => setCurrentScreen("Assignments")}
        >
          <BookOpen
            size={20}
            color={currentScreen === "Assignments" ? "#818cf8" : "#64748b"}
          />
          <Text
            style={[
              styles.tabLabel,
              currentScreen === "Assignments" && styles.tabLabelActive,
            ]}
          >
            Tasks
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.tabItem}
          onPress={() => setCurrentScreen("Fees")}
        >
          <DollarSign
            size={20}
            color={currentScreen === "Fees" ? "#818cf8" : "#64748b"}
          />
          <Text
            style={[
              styles.tabLabel,
              currentScreen === "Fees" && styles.tabLabelActive,
            ]}
          >
            Fees
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.tabItem}
          onPress={() => setCurrentScreen("PrintShop")}
        >
          <Printer
            size={20}
            color={currentScreen === "PrintShop" ? "#818cf8" : "#64748b"}
          />
          <Text
            style={[
              styles.tabLabel,
              currentScreen === "PrintShop" && styles.tabLabelActive,
            ]}
          >
            Print
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.tabItem}
          onPress={() => setCurrentScreen("AIRadar")}
        >
          <BrainCircuit
            size={20}
            color={currentScreen === "AIRadar" ? "#818cf8" : "#64748b"}
          />
          <Text
            style={[
              styles.tabLabel,
              currentScreen === "AIRadar" && styles.tabLabelActive,
            ]}
          >
            AI Radar
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

export default function App() {
  return (
    <SafeAreaProvider>
      <AuthProvider>
        <MainNavigator />
      </AuthProvider>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: "#020617",
  },
  screenContainer: {
    flex: 1,
  },
  tabBar: {
    flexDirection: "row",
    backgroundColor: "#0b0f19",
    borderTopWidth: 1,
    borderColor: "#1e293b",
    paddingVertical: 8,
    paddingHorizontal: 4,
    justifyContent: "space-around",
  },
  tabItem: {
    alignItems: "center",
    justifyContent: "center",
    flex: 1,
  },
  tabLabel: {
    fontSize: 10,
    color: "#64748b",
    marginTop: 4,
    fontWeight: "600",
  },
  tabLabelActive: {
    color: "#818cf8",
  },
});
