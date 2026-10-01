def fibonacci_sequence(n):
    sequence = [1, 1]
    while len(sequence) < n:
        next_value = sequence[-1] + sequence[-2]
        sequence.append(next_value)
    return sequence

# 테스트: 처음 10개의 항을 출력합니다.
fibonacci_10_terms = fibonacci_sequence(10)
print(fibonacci_10_terms)