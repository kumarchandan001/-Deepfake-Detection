import React, { useState } from 'react';
import { StyleSheet, Text, View, ScrollView, FlatList } from 'react-native';

export default function EvidenceViewerScreen() {
  const [evidence] = useState([
    { id: 'evd_1', filename: 'social_video_swap.mp4', status: 'VERIFIED_FAKE', time: '2026-05-27 23:10:00', custodian: 'Analyst Alpha' },
    { id: 'evd_2', filename: 'official_profile.jpg', status: 'VERIFIED_REAL', time: '2026-05-27 23:12:00', custodian: 'Analyst Beta' }
  ]);

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Case Evidence Vault</Text>
        <Text style={styles.headerSubtitle}>Forensic Chain of Custody Registry</Text>
      </View>

      <ScrollView style={styles.body}>
        <Text style={styles.sectionTitle}>Tracked Media Assets</Text>
        {evidence.map((item) => (
          <View key={item.id} style={styles.card}>
            <View style={styles.cardHeader}>
              <Text style={styles.filename} numberOfLines={1}>{item.filename}</Text>
              <Text style={[styles.badge, item.status === 'VERIFIED_REAL' ? styles.badgeReal : styles.badgeFake]}>
                {item.status}
              </Text>
            </View>
            <View style={styles.cardDetails}>
              <Text style={styles.detailText}>Custody Owner: {item.custodian}</Text>
              <Text style={styles.detailText}>Logged: {item.time}</Text>
              <Text style={styles.detailText}>ID: {item.id}</Text>
            </View>
          </View>
        ))}
        
        <Text style={styles.sectionTitle}>Active Custody Ledger</Text>
        <View style={styles.timelineContainer}>
          <View style={styles.timelineNode}>
            <View style={styles.timelineDot} />
            <View style={styles.timelineContent}>
              <Text style={styles.timelineTitle}>Acquisition - File checksum verified</Text>
              <Text style={styles.timelineSubtitle}>2026-05-27 23:10:00 by Analyst Alpha</Text>
            </View>
          </View>
          <View style={styles.timelineNode}>
            <View style={styles.timelineDot} />
            <View style={styles.timelineContent}>
              <Text style={styles.timelineTitle}>Model Pass - Waveform spectrogram analysis</Text>
              <Text style={styles.timelineSubtitle}>2026-05-27 23:11:15 by AI Engine</Text>
            </View>
          </View>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0B0F19',
    padding: 16,
  },
  header: {
    marginBottom: 20,
  },
  headerTitle: {
    color: '#60A5FA',
    fontSize: 18,
    fontWeight: 'bold',
  },
  headerSubtitle: {
    color: '#9CA3AF',
    fontSize: 11,
  },
  body: {
    flex: 1,
  },
  sectionTitle: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: 'bold',
    marginVertical: 12,
    textTransform: 'uppercase',
  },
  card: {
    backgroundColor: '#111827',
    borderWidth: 1,
    borderColor: '#1F2937',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  filename: {
    color: '#FFFFFF',
    fontWeight: 'bold',
    fontSize: 14,
    maxWidth: '60%',
  },
  badge: {
    fontSize: 10,
    fontWeight: 'bold',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  badgeReal: {
    backgroundColor: 'rgba(16, 185, 129, 0.2)',
    color: '#10B981',
  },
  badgeFake: {
    backgroundColor: 'rgba(239, 68, 68, 0.2)',
    color: '#EF4444',
  },
  cardDetails: {
    borderTopWidth: 1,
    borderTopColor: '#1F2937',
    paddingTop: 8,
  },
  detailText: {
    color: '#9CA3AF',
    fontSize: 11,
    marginBottom: 2,
  },
  timelineContainer: {
    paddingLeft: 8,
    borderLeftWidth: 1,
    borderLeftColor: '#1F2937',
    marginLeft: 8,
    marginTop: 8,
  },
  timelineNode: {
    position: 'relative',
    marginBottom: 16,
    paddingLeft: 12,
  },
  timelineDot: {
    position: 'absolute',
    left: -13,
    top: 4,
    width: 9,
    height: 9,
    borderRadius: 5,
    backgroundColor: '#3B82F6',
  },
  timelineContent: {
    backgroundColor: '#111827',
    borderRadius: 6,
    padding: 8,
  },
  timelineTitle: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: 'bold',
  },
  timelineSubtitle: {
    color: '#9CA3AF',
    fontSize: 10,
    marginTop: 2,
  },
});
