export const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-KE', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

export const formatDateTime = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('en-KE', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export const formatTime = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleTimeString('en-KE', {
    hour: '2-digit',
    minute: '2-digit',
  })
}