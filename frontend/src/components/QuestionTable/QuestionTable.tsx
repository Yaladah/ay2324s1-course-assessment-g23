import React, { ChangeEvent, FormEvent, Fragment, useState } from 'react'
import { type Question } from '../../api/questions.ts'
import {
    useAllQuestions,
    useDeleteQuestion,
    useStoreQuestion,
    useUpdateQuestion,
} from '../../stores/questionStore.ts'
import { useCurrentUser } from '../../stores/userStore.ts'
import '../../styles/AlertMessage.css'
import '../../styles/QuestionTable.css'
import AlertMessage from '../AlertMessage.tsx'
import QuestionEditableRow from './QuestionEditableRow.tsx'
import { QuestionForm } from './QuestionForm.tsx'
import QuestionReadOnlyRow from './QuestionReadOnlyRow.tsx'

const QuestionTable: React.FC = () => {
    const { data: user } = useCurrentUser()
    const { data: questions } = useAllQuestions()
    const storeQuestionMutation = useStoreQuestion()
    const updateQuestionMutation = useUpdateQuestion()
    const deleteQuestionMutation = useDeleteQuestion()
    const [addFormData, setAddFormData] = useState<Omit<Question, 'question_id'>>({
        title: '',
        description: '',
        category: '',
        complexity: 'Easy',
    })
    const [editFormData, setEditFormData] = useState<Question | null>(null)
    const [showQuestionForm, setShowQuestionForm] = useState(false)

    const handleEditFormChange = (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = event.target
        // @ts-ignore
        setEditFormData({
            ...editFormData,
            [name]: value,
        })
    }

    const handleAddFormSubmit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault()
        await storeQuestionMutation.mutateAsync(addFormData)
        setAddFormData({
            title: '',
            description: '',
            category: '',
            complexity: 'Easy',
        })
        setShowQuestionForm(false)
    }

    const handleEditFormSubmit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault()

        if (!editFormData) return
        await updateQuestionMutation.mutateAsync(editFormData)
        setEditFormData(null)
    }

    const handleEditClick = (event: React.MouseEvent<HTMLButtonElement>, question: Question) => {
        event.preventDefault()
        setEditFormData(question)
    }

    const handleCancelClick = () => {
        setEditFormData(null)
    }

    const handleFormChange = (updatedData: Omit<Question, 'question_id'>) => {
        setAddFormData(updatedData)
    }

    const handleDeleteClick = (questionId: string) => deleteQuestionMutation.mutate(questionId)

    const isMaintainer = user?.role === 'maintainer'
    return (
        <div className='question-container'>
            <h2>Questions</h2>
            <form onSubmit={handleEditFormSubmit}>
                <table className='question-table'>
                    <thead>
                        <tr>
                            <th id='id-header'>ID</th>
                            <th>Title</th>
                            <th>Category</th>
                            <th>Complexity</th>
                            {isMaintainer && <th>Actions</th>}
                        </tr>
                    </thead>
                    <tbody>
                        {questions.map((question) => (
                            <Fragment key={question.question_id}>
                                {editFormData &&
                                editFormData.question_id === question.question_id ? (
                                    <QuestionEditableRow
                                        editFormData={editFormData}
                                        handleEditFormChange={handleEditFormChange}
                                        handleCancelClick={handleCancelClick}
                                    />
                                ) : (
                                    <QuestionReadOnlyRow
                                        question={question}
                                        handleEditClick={handleEditClick}
                                        handleDeleteClick={handleDeleteClick}
                                        hasActions={isMaintainer}
                                    />
                                )}
                            </Fragment>
                        ))}
                    </tbody>
                </table>
            </form>

            {updateQuestionMutation.isError && (
                <AlertMessage variant='error'>
                    <h4>Oops! {updateQuestionMutation.error.detail}</h4>
                </AlertMessage>
            )}

            {deleteQuestionMutation.isError && (
                <AlertMessage variant='error'>
                    <h4>Oops! {deleteQuestionMutation.error.detail}</h4>
                </AlertMessage>
            )}
            {isMaintainer && (
                <>
                    <button onClick={() => setShowQuestionForm(true)}>Add a Question</button>
                    {showQuestionForm && (
                        <QuestionForm
                            initialData={addFormData}
                            onFormChange={handleFormChange}
                            onSubmit={handleAddFormSubmit}
                            onClose={() => setShowQuestionForm(false)}
                        />
                    )}
                    {storeQuestionMutation.isError && (
                        <AlertMessage variant='error'>
                            <h4>Oops! {storeQuestionMutation.error.detail}</h4>
                        </AlertMessage>
                    )}
                </>
            )}
        </div>
    )
}

export default QuestionTable
