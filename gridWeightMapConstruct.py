import scipy.stats
import salabase as sl


def gridWeightMapContruct(device, reports, table):
    
    # 0. 필요한 변수들 사전 정의
    grid_length = 20   # 단위 grid의 길이, cm단위, 변경가능
    room_width = 10    # 방의 가로 grid의 갯수, 변경가능
    room_length = 10   # 방의 세로 grid의 갯수, 변경가능
    room = []          # grid 단위로 방이 구현 될 리스트, 각 grid에는 grid의 center 좌표가 저장됨, 이 좌표를 바탕으로 모든 거리계산이 이루어 짐
    max_prob = 0       # 가장 큰 확률을 저장할 변수 
    max_prob_xy = sl.Pos(0,0)   # 가장 큰 확률을 가지는 grid의 x,y 좌표를 저장할 변수
    max_xy_list = []   # max_prob이 여러 개라면, 해당 x,y 좌표들을 저장할 리스트
    location = []      # 가장 큰 확률을 가지는 grid의 x,y 좌표를 return하기 위한 변수
    device = device    # return에 포함 될 device를 미리 저장
    """
   1)  -----------
       |         |   = grid 1개
       ----------- 
    
   2)  ( x, y )      = 각 grid의 center x,y 좌표
   
   3) 실제 방의 위치 정보를 나타내는 2차원 리스트 [10 grid x 10 grid] size의 room을 시각화 한 것
    ---------------------------------------------------
    | (10,10) | (10,30) | (10,50) |........| (10,190) |
    ---------------------------------------------------
    | (30,10) | (30,30) | (30,50) |........| (30,190) |
    ---------------------------------------------------
    .........(중간 생략)...............................
    ---------------------------------------------------
    | (190,10)| (190,30)| (190,50)|........| (190,190)|
    --------------------------------------------------
    """
    matrix_p = []      # 각 grid의 확률 값을 담을 리스트

    # 1. Grid 초기화
    for i in range(room_width):                # room의 각 grid마다 grid의 center 좌표를 저장
        temp = []
        for j in range(room_length):
            temp.append([i*20+10, j*20+10])   
        room.append(temp)
    
    for i in range(room_width):                # 확률이 저장될 matrix_p를 0으로 초기화
        temp = []
        for j in range(room_length):
            temp.append(0)
        matrix_p.append(temp)

    # Gradient Descent는 Centroid point + 그 근처 몇 개 점에서 뿌려 볼 것
    # 2. matrix_p에 확률값을 더하기

    # PowerDistanceTable에서 point 순차 선택
    for k in range(len(table)):
        # 각각의 grid에 접근, point의 avg_dist와 std_dev를 바탕으로 표준정규분포를 구함, 계산하여 나온 확률값을 grid에 누적하여 더함
        for i in range(room_width):
            for j in range(room_length):
                matrix_p[i][j] += scipy.stats.norm(0, table[k]["std_dev"]).pdf(
                    sl.distance2(
                        table[k]["point"].x, room[i][j][0], table[k]["point"].y, room[i][j][1]) - table[k]["avg_dist"])
                # room[i][j][0] = grid.x, room[i][j][1] = grid.y

    # 3. 3중 for loop을 통해 모든 grid의 확률 값을 구했으면, matrix prob에서 가장 큰 값이 들어있는 grid를 찾아내어 좌표를 return
    # 같은 값을 가진 cell이 여러개라면 그 cell들의 중간 좌표를 return
    for i in range(room_width):
        for j in range(room_length):
            if matrix_p[i][j] > max_prob:
                max_prob = matrix_p[i][j]
                max_prob_xy = [room[i][j][0], room[i][j][1]]  # max_prob을 가지고 있는 grid의 x,y좌표를 저장
                max_xy_list.clear()            # 기존 max_prob보다 더 큰 값을 가진 grid를 찾았으면, 기존의 max_xy_list를 비우고 새로 시작
                max_xy_list.append(max_prob_xy)
            elif matrix_p[i][j] == max_prob:
                max_prob_xy = [room[i][j][0], room[i][j][1]] 
                max_xy_list.append(max_prob_xy)     # 기존 max_prob와 같은 값을 가진 grid를 찾았으면, 기존의 max_xy_list에 해당 x,y좌표를 추가
                
    if len(max_xy_list) == 1:      # 가장 큰 확률값을 가진 grid가 1개일 때
        location = max_xy_list
    elif len(max_xy_list) >= 2:     # 가장 큰 확률값을 가진 grid가 1개 이상일 때, 해당 grid들의 중간 좌표를 return
        sum_x = 0
        sum_y = 0
        for i in max_xy_list:
            sum_x += i[0]
            sum_y += i[1]
        final_x = sum_x/len(max_xy_list)
        final_y = sum_y/len(max_xy_list)
        location = [final_x, final_y]

    print('\n========================================')
    print('=== Grid Weight Map Construct Result ===')
    print('========================================')
    print('IoT Device: ' + str(device))
    print('IoT Device location: ' + str(location))

    return device, location
