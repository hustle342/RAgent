import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons'; // İkonlar için (Eğer expo yoksa alternatif eklenecek)

// Ekranlar
import ChatScreen from './src/screens/ChatScreen';

const Tab = createBottomTabNavigator();

const App = () => {
  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <Tab.Navigator
          screenOptions={({ route }) => ({
            tabBarIcon: ({ focused, color, size }) => {
              let iconName;

              if (route.name === 'Chat') {
                iconName = focused ? 'chatbubble-ellips' : 'chatbubble-ellips-outline';
              } else if (route.name === 'Documents') {
                iconName = focused ? 'document-text' : 'document-text-outline';
              } else if (route.name === 'Quiz') {
                iconName = focused ? 'school' : 'school-outline';
              }

              return <Ionicons name={iconName} size={size} color={color} />;
            },
            tabBarActiveTintColor: '#007AFF',
            tabBarInactiveTintColor: 'gray',
            headerShown: false,
          })}
        >
          <Tab.Screen name="Chat" component={ChatScreen} options={{ title: 'Sohbet' }} />
          {/* Gelecekte eklenecek ekranlar */}
          <Tab.Screen
            name="Documents"
            component={ChatScreen} // Geçici olarak aynı ekranı veriyoruz
            options={{ title: 'Belgeler' }}
          />
          <Tab.Screen
            name="Quiz"
            component={ChatScreen} // Geçici olarak aynı ekranı veriyoruz
            options={{ title: 'Test' }}
          />
        </Tab.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
};

export default App;
