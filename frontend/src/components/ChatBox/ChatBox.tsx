import { Add, Circle, Remove } from '@mui/icons-material'
import { motion, useAnimation } from 'framer-motion'
import React, { useEffect, useRef, useState } from 'react'
import { useParams } from 'react-router'
import { useCurrentUser } from '../../stores/userStore.ts'
import '../../styles/Room.css'
import ChatMessage from './ChatMessage.tsx'

/** URL for communication websocket API. */
const COMMUNICATION_API_URL =
    `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}` +
    '/api/communication'

type ChatMessage = {
    sender: string // The sender's name or identifier
    text: string // The message content
    msg_type: string
}

const ChatBox: React.FC = () => {
    const { roomId } = useParams()
    const [socket, setSocket] = useState<WebSocket | null>(null)
    const { data: user, isFetching: isFetchingCurrentUser } = useCurrentUser()
    const constraintsRef = useRef(null)
    const [formValue, setFormValue] = useState('')
    const [isMinimized, setIsMinimized] = useState(false)
    const chatHeaderControls = useAnimation()
    const [chatMessages, setChatMessages] = useState<ChatMessage[]>([])
    const messagesEndRef = useRef<HTMLDivElement | null>(null)

    useEffect(() => {
        // Check if user is not null and not fetching
        if (user !== null) {
            const socket = new WebSocket(
                COMMUNICATION_API_URL + `/communication/${roomId}/${user.username}`
            )
            setSocket(socket)

            return () => {
                socket.close()
            }
        }
    }, [user, roomId])

    useEffect(() => {
        if (socket == null) return

        socket.onopen = () => {
            console.log('WebSocket connection is open')
            const user_id = user?.username
            const userJoinMessage = JSON.stringify({
                event: 'join-room',
                sender: user_id,
            })
            socket.send(userJoinMessage)

            const newMessage = {
                sender: user_id,
                text: '',
                msg_type: 'join',
            }

            setChatMessages((prevChatMessages) => [...prevChatMessages, newMessage])
        }

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data)

            if (data.event == 'receive-message') {
                const text = data.message
                const sender_id = data.sender
                const newMessage = { sender: sender_id, text: text, msg_type: 'message' }
                setChatMessages((prevChatMessages) => [...prevChatMessages, newMessage])
            } else if (data.event == 'join-room') {
                const sender_id = data.sender
                const newMessage = { sender: sender_id, text: '', msg_type: 'join' }
                setChatMessages((prevChatMessages) => [...prevChatMessages, newMessage])
            } else if (data.event == 'leave-room') {
                const sender_id = data.sender
                const newMessage = { sender: sender_id, text: '', msg_type: 'leave' }
                setChatMessages((prevChatMessages) => [...prevChatMessages, newMessage])
            } else if (data.event == 'full-room') {
                console.log('Room is full')
                socket.close()
            }
        }

        socket.onclose = (event) => {
            const userLeaveMessage = JSON.stringify({
                event: 'leave-room',
                sender: user?.username,
            })
            socket.send(userLeaveMessage)

            const newMessage = {
                sender: user_id,
                text: '',
                msg_type: 'leave',
            }

            setChatMessages((prevChatMessages) => [...prevChatMessages, newMessage])
        }

        scrollToBottom()
    }, [socket])

    useEffect(() => {
        scrollToBottom()
    }, [chatMessages]) // Assuming `chatMessages` is the list/array containing your chat messages

    const chatBoxVariants = {
        minimized: { height: '50px' },
        expanded: { height: '500px' },
    }

    const sendMessage = (event: React.FormEvent) => {
        event.preventDefault()
        if (!socket) return // Ensure the socket is available

        // Create the payload in the required format
        const payload = JSON.stringify({
            event: 'send-message',
            sender: user?.username,
            message: formValue,
        })

        // Send the message through the WebSocket
        socket.send(payload)

        setChatMessages((prevChatMessages) => [
            ...prevChatMessages,
            {
                sender: user?.username as string,
                text: formValue,
                msg_type: 'message',
            } as ChatMessage,
        ])

        setFormValue('')
    }

    const toggleMinimize = (e: React.MouseEvent) => {
        e.stopPropagation()
        setIsMinimized(!isMinimized)
    }

    const handleHeaderClick = () => {
        if (isMinimized) {
            chatHeaderControls.start({ y: -10 }).then(() => {
                chatHeaderControls.start({ y: 0 })
            })
        }
    }

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    return (
        <motion.div ref={constraintsRef}>
            <motion.div
                className='chat-box'
                style={{ display: 'flex' }}
                animate={isMinimized ? 'minimized' : 'expanded'}
                variants={chatBoxVariants}
                drag='x'
                dragElastic={false}
                dragMomentum={false}
                dragConstraints={constraintsRef}
            >
                <motion.div
                    style={{ alignItems: 'center', width: '100%' }}
                    animate={chatHeaderControls}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleHeaderClick}
                >
                    <div className='chat-header'>
                        {isMinimized ? (
                            <Add
                                sx={{ marginRight: 'auto', cursor: 'pointer' }}
                                onClick={toggleMinimize}
                            />
                        ) : (
                            <Remove
                                sx={{ marginRight: 'auto', cursor: 'pointer' }}
                                onClick={toggleMinimize}
                            />
                        )}
                        <Circle sx={{ alignSelf: 'right', color: '#00b8a2', fontSize: '10px' }} />
                        <h3 style={{ color: 'white', margin: '12px' }}>Chat Room</h3>
                    </div>
                    <div className='chat-background'>
                        {chatMessages.map((message, index) => (
                            <ChatMessage
                                key={index}
                                text={message.text}
                                sender={message.sender}
                                msg_type={message.msg_type}
                            />
                        ))}
                        <div ref={messagesEndRef} />
                    </div>
                    <div style={{ backgroundColor: 'white', padding: '10px' }}>
                        <form onSubmit={sendMessage}>
                            <input
                                value={formValue}
                                onChange={(e) => setFormValue(e.target.value)}
                                placeholder='Send a message'
                            />

                            <button type='submit' disabled={!formValue}>
                                Send
                            </button>
                        </form>
                    </div>
                </motion.div>
            </motion.div>
        </motion.div>
    )
}

export default ChatBox
