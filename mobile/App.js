import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import Ionicons from 'react-native-vector-icons/Ionicons'; // Use react-native-vector-icons instead of @expo/vector-icons
import { Text } from 'react-native';

// Ekranlar
import ChatScreen from './src/screens/ChatScreen';
import DocumentsScreen from './src/screens/DocumentsScreen';
import QuizScreen from './src/screens/QuizScreen';
import HomeScreen from './src/screens/HomeScreen';
import SettingsScreen from './src/screens/SettingsScreen';
import SummaryScreen from './src/screens/SummaryScreen';
import { AppProvider } from './src/context/AppContext';

const Tab = createBottomTabNavigator();

const App = () => {
  return (
    <SafeAreaProvider>
      <AppProvider>
      <NavigationContainer>
        <Tab.Navigator
          screenOptions={({ route }) => ({
            tabBarIcon: ({ focused, color, size }) => {
              // Emoji icons for action tabs and settings; keep Home using Ionicons
              if (route.name === 'Ask') return <Text style={{ fontSize: size }}>{'❓'}</Text>;
              if (route.name === 'CreateTest') return <Text style={{ fontSize: size }}>{'📝'}</Text>;
              if (route.name === 'Summary') return <Text style={{ fontSize: size }}>{'📄'}</Text>;
              if (route.name === 'Settings') return <Text style={{ fontSize: size }}>{'⚙️'}</Text>;
              if (route.name === 'Home') return <Ionicons name={focused ? 'home' : 'home-outline'} size={size} color={color} />;
              // fallback
              return <Ionicons name={'ellipse'} size={size} color={color} />;
            },
            tabBarActiveTintColor: '#ffffff',
            tabBarInactiveTintColor: '#888888',
            tabBarStyle: { backgroundColor: '#000000' },
            headerShown: false,
            tabBarShowLabel: true,
          })}
        >
          {/* Keep Home visible exactly as before */}
          <Tab.Screen name="Home" component={HomeScreen} options={{ title: 'Ana Sayfa' }} />

          {/* Primary action buttons in bottom bar */}
          <Tab.Screen name="Ask" component={ChatScreen} options={{ title: 'Soru Sor' }} />
          <Tab.Screen name="CreateTest" component={QuizScreen} options={{ title: 'Test Oluştur' }} />
          <Tab.Screen name="Summary" component={SummaryScreen} options={{ title: 'Özet Çıkar' }} />

          {/* Settings visible with emoji */}
          <Tab.Screen name="Settings" component={SettingsScreen} options={{ title: 'Ayarlar' }} />

          {/* Keep Documents and (optional) Chat hidden from tab bar if not desired */}
          <Tab.Screen name="Documents" component={DocumentsScreen} options={{ title: 'Belgeler', tabBarButton: () => null }} />
        </Tab.Navigator>
      </NavigationContainer>
      </AppProvider>
    </SafeAreaProvider>
  );
};

export default App;
