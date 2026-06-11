export type ChatUserRole = "driver" | "passenger";

export type ChatUser = {
  id: number;
  name: string;
  role: ChatUserRole;
};

export type ChatParticipant = ChatUser & {
  reservationStatus: "confirmed" | "pending" | "cancelled";
};

export type ChatMessage = {
  id: number;
  tripId: number;
  senderId: number;
  senderName: string;
  senderRole: ChatUserRole;
  content: string;
  sentAt: string;
};