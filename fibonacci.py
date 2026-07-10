def fibonacci(n: int) -> list[int]:
    """
    주어진 정수 n까지의 피보나치 수열을 생성하여 리스트로 반환합니다.
    피보나치 수열은 0, 1, 1, 2, 3, 5, 8... 로 진행됩니다.

    Args:
        n (int): 생성할 항의 개수 (n >= 1).

    Returns:
        list[int]: 피보나치 수열 리스트. n이 0 이하일 경우 빈 리스트를 반환합니다.
    """
    if n <= 0:
        return []
    elif n == 1:
        # 첫 번째 항만 요청 시 [0]을 반환하는 것이 일반적입니다.
        return [0]
    else:
        sequence = [0, 1]
        # 이미 두 개의 항(0과 1)이 있으므로, n-2 번 반복합니다.
        for i in range(2, n):
            next_fib = sequence[i - 1] + sequence[i - 2]
            sequence.append(next_fib)
        return sequence

# --- 테스트 코드 예시 ---
if __name__ == "__main__":
    print("=== 피보나치 수열 생성기 ===")

    # 1. 8번째 항까지 생성 (0부터 시작하여 총 8개 항: 0, 1, 1, 2, 3, 5, 8, 13)
    N_TEST = 8
    fib_list = fibonacci(N_TEST)
    print(f"\n[테스트 1] {N_TEST}번째 항까지 생성된 수열 (총 {len(fib_list)}개):")
    print(" -> " + ", ".join(map(str, fib_list)))

    # 2. 작은 값 테스트 (3항)
    N_SMALL = 3
    fib_small = fibonacci(N_SMALL)
    print(f"\n[테스트 2] {N_SMALL}번째 항까지 생성된 수열: {fib_small}")

    # 3. 경계값 테스트 (0항)
    N_ZERO = 0
    fib_zero = fibonacci(N_ZERO)
    print(f"\n[테스트 3] {N_ZERO}번째 항까지 생성된 수열: {fib_zero}")