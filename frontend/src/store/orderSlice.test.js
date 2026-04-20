import reducer from './orderSlice'

describe('orderSlice reducer', () => {
  it('returns initial state', () => {
    const state = reducer(undefined, { type: '@@INIT' })
    expect(state.active).toEqual([])
    expect(state.history).toEqual([])
    expect(state.loading).toBe(false)
  })
})
