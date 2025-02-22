import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import MatchBar from '../components/MatchBar.tsx'
import Navbar from '../components/Navbar.tsx'
import { QuestionTable } from '../components/QuestionTable/QuestionTable.tsx'
import { TimerProvider } from '../components/TimerProvider.tsx'
import { useSessionDetails } from '../stores/sessionStore.ts'

const Questions = () => {
    const { data: sessionDetails, isFetching: isFetchingSession } = useSessionDetails()

    const navigate = useNavigate()

    // Redirect if not logged in.
    useEffect(() => {
        const isNotLoggedIn = sessionDetails === null
        if (isNotLoggedIn && !isFetchingSession) navigate('/')
    }, [sessionDetails, isFetchingSession, navigate])

    return (
        <>
            <Navbar />
            <div className='question-page-container'>
                <TimerProvider>
                    <MatchBar />
                </TimerProvider>
                <QuestionTable />
            </div>
        </>
    )
}

export default Questions
