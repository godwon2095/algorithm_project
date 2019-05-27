from django.shortcuts import render, redirect, get_object_or_404
from .models import *
import pdb, random, time


def dynamic(request):
    algorithm = Algorithm.objects.get(name="dynamic")
    records = None
    if algorithm is not None:
        records = Record.objects.filter(algorithm=algorithm).order_by('n_size')
    return render(request, 'algorithms/dynamic.html', {'records': records})


def boyer_moore(request):
    algorithm = Algorithm.objects.get(name="boyer_moore")
    records = None
    if algorithm is not None:
        records = Record.objects.filter(algorithm=algorithm).order_by('n_size')
    return render(request, 'algorithms/boyer_moore.html', {'records': records})


def calc_dynamic(request):
    if request.method == "POST":
        # 폼으로 부터 넘어온 M, N, L 값을 각각의 변수에 담아 둔다.
        n_val = int(request.POST.get('N'))
        l_val = int(request.POST.get('L'))
        m_val = int(request.POST.get('M'))

        myGenomeSeq = generateSequences(n_val)
        shortReads = generateShortReads(n_val, l_val, m_val, myGenomeSeq)

        start_at = time.clock()
        for index, short_read in enumerate(shortReads):
            dynamicSearch(myGenomeSeq, short_read, n_val, l_val)
        end_at = time.clock()

        _time = (end_at-start_at)*1000.0
        print('Dynamic Search took %0.5f ms' % (_time))

        getRecordObject("dynamic", n_val, l_val, m_val, _time)
        
        return redirect('algorithms:dynamic')



def calc_boyer_moore(request):
    if request.method == "POST":
        # 폼으로 부터 넘어온 M, N, L 값을 각각의 변수에 담아 둔다.
        n_val = int(request.POST.get('N'))
        l_val = int(request.POST.get('L'))
        m_val = int(request.POST.get('M'))
        
        myGenomeSeq = generateSequences(n_val)
        shortReads = generateShortReads(n_val, l_val, m_val, myGenomeSeq)

        start_at = time.clock()
        for short_read in shortReads:
            boyerMooreSearch(myGenomeSeq, short_read, n_val, l_val)
        end_at = time.clock()

        _time = (end_at-start_at)*1000.0
        print('Boyer Moore Search took %0.5f ms' % (_time))

        getRecordObject("boyer_moore", n_val, l_val, m_val, _time)

        return redirect('algorithms:boyer_moore')


## genome sequence 를 만들어 내는 함수
def generateSequences(N):
    bases = ('A', 'C', 'G', 'T')
    seq = ''.join([random.choice(bases) for _ in range(N)])
    return seq


## short read 를 뽑아내는 함수
def generateShortReads(N, L, M, genomeSeq):
    rand_indexes = random.sample(range(N - L), M)
    short_reads = []
    for index in rand_indexes:
        short_read = genomeSeq[index:index+L]
        short_reads.append(short_read)
    return short_reads


def dynamicSearch(text, pattern, N, L):
    _max_ = 0 
    index = 0
    # dynamic table 을 만들어준다 (N행 L열의 테이블)
    dp = [[0]* (L + 1) for i in range(N + 1)]

    for i in range(0, N + 1):
        for j in range(0, L + 1):
            # 특정 위치의 문자가 같은 경우에 해당 값을 1 더해준다
            if text[i - 1] == pattern[j - 1]: 
                dp[i][j] = dp[i - 1][j - 1] + 1
            
            # 동시에 _max_ 보다 특정 dp[i][j]가 커졌을 경우에만 값을 바꾸어준다
            # 그리고 그때의 index를 찾을 수 있게 된다.
            if dp[i][j] > _max_:
                _max_ = dp[i][j]
                index = i
    
    print("found at {}".format(index))
    return index


## 착한 접미부의 index를 가져오는 함수
def getGoodSuffixIndex(badChar, suffix, pattern):
    # [::-1]를 이용해서 패턴의 오른쪽부터 검사한다
    for i in range(1, len(pattern)+1)[::-1]:
        check = True
        for j in range(0, len(suffix)):
            # pattern_index 에 index 값을 집어 넣고 일치하는 겨우는 그 값만큼 이동
            # 일치하지 않는 경우는 해당 패턴 길이만큼 이동시켜준다
            pattern_index = i - len(suffix) - 1 + j
            if pattern_index < 0 or suffix[j] == pattern[pattern_index]:
                pass
            else:
                check = False
        pattern_index = i - len(suffix) - 1
        if check and (pattern_index <= 0 or pattern[pattern_index-1] != badChar):
            return len(pattern)- i + 1


## 좋은 접미부 테이블을 생성하는 부분
def generateGoodSuffixTable(pattern):
    GoodSuffixTable = {}
    goodSuffix = ""
    patternLength = len(pattern)

    # 패턴을 돌면서 착한 접미부 index를 가져오는 함수를 이용하여 접미부 테이블을 채운다
    for i in range(0, patternLength):
        GoodSuffixTable[len(goodSuffix)] = getGoodSuffixIndex(pattern[patternLength - i - 1], goodSuffix, pattern)
        goodSuffix = pattern[patternLength - i - 1] + goodSuffix
    return GoodSuffixTable


## 나쁜 문자 테이블을 생성하는 부분
def generateBadCharTable(pattern):
    BadCharTable = {}
    
    # dictionary type 에 특정 문자를 key 와 value 형태로 저장
    for i in range(0, len(pattern) - 1):
        BadCharTable[pattern[i]] = len(pattern) - i - 1

    return BadCharTable

    
## 보이어 무어 알고리즘
def boyerMooreSearch(text, pattern, N, L):
    # 위에서 만든 함수로 나쁜 문자 테이블과 좋은 접미부 테이블을 만든다
    badCharTable = generateBadCharTable(pattern)
    goodSuffixTable = generateGoodSuffixTable(pattern)

    i = 0
    while i < N - L + 1:
        j = L

        # 문자가 일치하는 경우 j를 줄여나간다 j 가 0이 된 순간은 일치하는 문자열을 찾게 되는 경우
        while j > 0 and pattern[j-1] == text[i+j-1]:
            j -= 1

        # j 가 아직 양수인 경우에 나쁜문자테이블과 좋은접미부 테이블 중 더 크게 shift 할 수 있는 정도를 취해서 이동한다
        if j > 0:
            # get 을 사용하면 만약 해당 문자를 얻지 못한경우 pattern 의 길이만큼 이동하게 된다
            badCharShift = badCharTable.get(text[i+j-1], len(pattern))
            goodSuffixShift = goodSuffixTable[L-j]
            shift = max(badCharShift, goodSuffixShift)
            i += shift
        else:
            print("found at {}".format(i))
            return i
    return -1


def getRecordObject(algorithm_name, n_val, l_val, m_val, _time):
    algorithm = Algorithm.objects.get(name=algorithm_name)

    if algorithm is None:
        algorithm = Algorithm.objects.create(name=algorithm_name)

    Record.objects.create(
        algorithm = algorithm,
        m_size = m_val,
        l_size = l_val,
        n_size = n_val,
        time = _time
    )