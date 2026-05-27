import React, { useState } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, Image, ActivityIndicator } from 'react-native';

export default function VerificationScreen() {
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleVerifyPress = () => {
    setAnalyzing(true);
    setResult(null);

    // Simulate mobile API upload workflow response
    setTimeout(() => {
      setAnalyzing(false);
      setResult({
        verdict: 'REAL',
        confidence: '97.4%',
        media_type: 'IMAGE',
        filename: 'captured_media.jpg',
      });
    }, 2000);
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Antigravity Trust Mobile</Text>
        <Text style={styles.headerSubtitle}>Real-time Media Verification</Text>
      </View>

      <View style={styles.previewBox}>
        <Image 
          source={{ uri: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=400' }}
          style={styles.previewImage}
        />
        <View style={styles.viewfinder} />
      </View>

      <View style={styles.actions}>
        {analyzing ? (
          <View style={styles.loadingBox}>
            <ActivityIndicator size="large" color="#3B82F6" />
            <Text style={styles.actionText}>Running Forensic Models...</Text>
          </View>
        ) : (
          <TouchableOpacity style={styles.verifyButton} onPress={handleVerifyPress}>
            <Text style={styles.buttonText}>Capture & Verify Media</Text>
          </TouchableOpacity>
        )}
      </View>

      {result && (
        <View style={[styles.resultCard, result.verdict === 'REAL' ? styles.resultReal : styles.resultFake]}>
          <Text style={styles.resultVerdict}>Verdict: {result.verdict}</Text>
          <Text style={styles.resultDetail}>Confidence: {result.confidence}</Text>
          <Text style={styles.resultDetail}>Source File: {result.filename}</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0B0F19',
    padding: 20,
    justifyContent: 'space-between',
  },
  header: {
    marginTop: 20,
    alignItems: 'center',
  },
  headerTitle: {
    color: '#60A5FA',
    fontSize: 20,
    fontWeight: 'bold',
  },
  headerSubtitle: {
    color: '#9CA3AF',
    fontSize: 12,
  },
  previewBox: {
    flex: 1,
    maxHeight: 350,
    borderWidth: 2,
    borderColor: '#1F2937',
    borderRadius: 12,
    overflow: 'hidden',
    position: 'relative',
    marginVertical: 20,
  },
  previewImage: {
    width: '100%',
    height: '100%',
  },
  viewfinder: {
    position: 'absolute',
    top: '15%',
    left: '15%',
    right: '15%',
    bottom: '15%',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.4)',
    borderRadius: 8,
    borderStyle: 'dashed',
  },
  actions: {
    alignItems: 'center',
    marginBottom: 10,
  },
  verifyButton: {
    backgroundColor: '#2563EB',
    paddingVertical: 14,
    paddingHorizontal: 28,
    borderRadius: 8,
    width: '100%',
    alignItems: 'center',
  },
  buttonText: {
    color: '#FFFFFF',
    fontWeight: 'bold',
    fontSize: 16,
  },
  loadingBox: {
    alignItems: 'center',
  },
  actionText: {
    color: '#9CA3AF',
    marginTop: 10,
    fontSize: 14,
  },
  resultCard: {
    borderRadius: 8,
    padding: 16,
    borderWidth: 1,
    marginBottom: 20,
  },
  resultReal: {
    backgroundColor: 'rgba(16, 185, 129, 0.1)',
    borderColor: '#10B981',
  },
  resultFake: {
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
    borderColor: '#EF4444',
  },
  resultVerdict: {
    color: '#FFFFFF',
    fontWeight: 'bold',
    fontSize: 18,
    marginBottom: 4,
  },
  resultDetail: {
    color: '#D1D5DB',
    fontSize: 12,
  },
});
