import React from 'react'
import { useCurrentUser } from '../../stores/userStore.ts'
import '../../styles/Room.css'

interface ChatMessageProps {
    text: string
    sender: string
    type: string
}

const ChatMessage: React.FC<ChatMessageProps> = ({ text, sender, msg_type }) => {
    const { data: user } = useCurrentUser()

    // Check if the message sender is the current user
    const isSentByCurrentUser = user && sender === user.username
    if (msg_type == 'message') {
        return (
            <div className={`message-item-${isSentByCurrentUser ? 'sent' : 'received'}`}>
                <div className={`text-box-${isSentByCurrentUser ? 'sent' : 'received'}`}>
                    {text}
                </div>
                {!isSentByCurrentUser && <div className='sender-info'>{sender}</div>}
            </div>
        )
    } else if (msg_type == 'join') {
        return (
            <div className='message-item-join-leave'>
                <div className='message-box-join-leave'>{`${sender} has joined`}</div>
            </div>
        )
        // return <div className='message-join-leave'>{`${sender} has joined`}</div>
    } else if (msg_type == 'leave') {
        return (
            <div className='message-item-join-leave'>
                <div className='message-box-join-leave'>{`${sender} has left`}</div>
            </div>
        )
    }
}

export default ChatMessage
