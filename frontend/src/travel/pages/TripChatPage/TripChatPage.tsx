import { useMemo, useState } from "react";
import izilineLogo from "../../../assets/iziline.png";
import type { ChatMessage, ChatParticipant, ChatUser } from "../../../types/chat";
import "./TripChatPage.css";

const currentUser: ChatUser = {
  id: 2,
  name: "Ana Souza",
  role: "passenger",
};

const trip = {
  id: 35,
  origin: "Terminal Rodoviário Lucídio Portella, Teresina",
  destination: "Terminal Rodoviário de Floriano",
  departureAt: "2026-06-12T07:30:00-03:00",
};

const participants: ChatParticipant[] = [
  {
    id: 1,
    name: "Carlos Lima",
    role: "driver",
    reservationStatus: "confirmed",
  },
  {
    id: 2,
    name: "Ana Souza",
    role: "passenger",
    reservationStatus: "confirmed",
  },
  {
    id: 3,
    name: "Bruno Alves",
    role: "passenger",
    reservationStatus: "confirmed",
  },
  {
    id: 4,
    name: "Marina Costa",
    role: "passenger",
    reservationStatus: "pending",
  },
];

const initialMessages: ChatMessage[] = [
  {
    id: 1,
    tripId: trip.id,
    senderId: 1,
    senderName: "Carlos Lima",
    senderRole: "driver",
    content: "Bom dia! Vou sair do terminal às 7h30 em ponto.",
    sentAt: "2026-06-11T08:15:00-03:00",
  },
  {
    id: 2,
    tripId: trip.id,
    senderId: 2,
    senderName: "Ana Souza",
    senderRole: "passenger",
    content: "Perfeito. Podemos nos encontrar perto da entrada principal?",
    sentAt: "2026-06-11T08:18:00-03:00",
  },
  {
    id: 3,
    tripId: trip.id,
    senderId: 3,
    senderName: "Bruno Alves",
    senderRole: "passenger",
    content: "Também estarei lá. Vou chegar uns 10 minutos antes.",
    sentAt: "2026-06-11T08:22:00-03:00",
  },
  {
    id: 4,
    tripId: trip.id,
    senderId: 1,
    senderName: "Carlos Lima",
    senderRole: "driver",
    content: "Combinado. Fico aguardando vocês no recuo de embarque.",
    sentAt: "2026-06-11T08:30:00-03:00",
  },
];

function formatMessageTime(value: string) {
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function formatTripDate(value: string) {
  return new Intl.DateTimeFormat("pt-BR", {
    weekday: "long",
    day: "2-digit",
    month: "long",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function getParticipantLabel(participant: ChatParticipant) {
  if (participant.role === "driver") {
    return "Motorista";
  }

  return participant.reservationStatus === "confirmed"
    ? "Passageiro confirmado"
    : "Reserva pendente";
}

export function TripChatPage() {
  const [messages, setMessages] = useState(initialMessages);
  const [messageText, setMessageText] = useState("");

  const currentParticipant = participants.find(
    (participant) => participant.id === currentUser.id
  );

  const canUseChat = Boolean(
    currentParticipant &&
      (currentParticipant.role === "driver" ||
        currentParticipant.reservationStatus === "confirmed")
  );

  const confirmedParticipants = participants.filter(
    (participant) =>
      participant.role === "driver" || participant.reservationStatus === "confirmed"
  );

  const orderedMessages = useMemo(
    () =>
      [...messages].sort(
        (firstMessage, secondMessage) =>
          new Date(firstMessage.sentAt).getTime() -
          new Date(secondMessage.sentAt).getTime()
      ),
    [messages]
  );

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const content = messageText.trim();

    if (!content || !canUseChat) {
      return;
    }

    const nextMessage: ChatMessage = {
      id: Date.now(),
      tripId: trip.id,
      senderId: currentUser.id,
      senderName: currentUser.name,
      senderRole: currentUser.role,
      content,
      sentAt: new Date().toISOString(),
    };

    setMessages((currentMessages) => [...currentMessages, nextMessage]);
    setMessageText("");
  }

  return (
    <main className="trip-chat-page">
      <section className="trip-chat-shell" aria-labelledby="trip-chat-title">
        <aside className="trip-chat-sidebar">
          <img className="trip-chat-logo" src={izilineLogo} alt="Iziline" />

          <div className="trip-chat-summary">
            <span>Viagem confirmada</span>
            <h1 id="trip-chat-title">Chat da carona</h1>
            <p>{formatTripDate(trip.departureAt)}</p>
            <strong>{trip.origin}</strong>
            <span>até</span>
            <strong>{trip.destination}</strong>
          </div>

          <div className="trip-chat-participants" aria-label="Participantes do chat">
            <h2>Participantes</h2>
            {confirmedParticipants.map((participant) => (
              <div className="trip-chat-participant" key={participant.id}>
                <span>{participant.name}</span>
                <small>{getParticipantLabel(participant)}</small>
              </div>
            ))}
          </div>
        </aside>

        <section className="trip-chat-card" aria-label="Mensagens da viagem">
          {!canUseChat && (
            <div className="trip-chat-locked" role="alert">
              O chat só fica disponível para o motorista e passageiros com reserva confirmada nesta viagem.
            </div>
          )}

          <div className="trip-chat-messages">
            {orderedMessages.map((message) => {
              const isOwnMessage = message.senderId === currentUser.id;

              return (
                <article
                  className={
                    isOwnMessage
                      ? "chat-message chat-message--own"
                      : "chat-message chat-message--other"
                  }
                  key={message.id}
                >
                  <div className="chat-message__bubble">
                    <header>
                      <strong>{message.senderName}</strong>
                      <span>{message.senderRole === "driver" ? "Motorista" : "Passageiro"}</span>
                    </header>
                    <p>{message.content}</p>
                    <time dateTime={message.sentAt}>{formatMessageTime(message.sentAt)}</time>
                  </div>
                </article>
              );
            })}
          </div>

          <form className="trip-chat-composer" onSubmit={handleSubmit}>
            <label htmlFor="chatMessage">Mensagem</label>
            <div className="trip-chat-composer__row">
              <input
                id="chatMessage"
                type="text"
                placeholder={
                  canUseChat
                    ? "Digite sua mensagem"
                    : "Chat indisponível para esta reserva"
                }
                value={messageText}
                disabled={!canUseChat}
                onChange={(event) => setMessageText(event.target.value)}
              />
              <button type="submit" disabled={!canUseChat || !messageText.trim()}>
                Enviar
              </button>
            </div>
          </form>
        </section>
      </section>
    </main>
  );
}