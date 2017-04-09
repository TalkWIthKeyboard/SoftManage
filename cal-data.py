# -*- coding: utf-8 -*-
import csv
import sys, getopt

reload(sys)

sys.setdefaultencoding('utf8')

# 风险数组
global riskList
# 决策树数组
global treeList
# 事故描述数组
global problemList
# 事故的个数
global problem_num
# 花费数组
global costList
# 输出文件
global file
cost_quota = 9.5

swith = ['bad choice', 'good choice', 'best choice']
riskName = ['disaster', 'disease', 'goods', 'route', 'settlement', 'teamwork', 'transportation', 'weather']


class TreeNode:
    # 父亲节点，本节点映射的数组索引
    fa = -1
    index = -1
    choose = -1
    # 左，中，右儿子
    l = -1
    m = -1
    r = -1
    # 总风险评分和总花费
    riskScoreAll = 0
    costAll = 0
    haveSon = True

    def __init__(self, rs, c):
        self.riskScoreAll = rs
        self.costAll = c

    def change(self, rs, c, choose):
        self.riskScoreAll = rs
        self.costAll = c
        self.choose = choose


class Choose:
    # 风险发生的可能性
    riskProbability = 0
    # 影响因子
    influenceFactor = 0
    # 花费
    cost = 0

    def __init__(self, rp, iF, cost):
        self.riskProbability = rp
        self.influenceFactor = iF
        self.cost = cost


class Risk:
    # 三个选择
    chooseOne = Choose(0, 0, 0)
    chooseTwo = Choose(0, 0, 0)
    chooseThree = Choose(0, 0, 0)

    def __init__(self, one, two, three):
        self.chooseOne = one
        self.chooseTwo = two
        self.chooseThree = three


def preTreateData(csv_name):
    """
    预处理数据
    :return:
    """
    csv_reader = csv.reader(open(csv_name))
    index = 0
    for row in csv_reader:
        if index != 0:
            risk = Risk(
                Choose(float(row[2]) * float(row[4]), float(row[3]), float(row[7])),
                Choose(float(row[2]) * float(row[5]), float(row[3]), float(row[8])),
                Choose(float(row[2]) * float(row[6]), float(row[3]), float(row[9]))
            )
            problemList.append(row[1])
            riskList.append(risk)
        index += 1
    problem_num = index


def makeDecisionTree(fa, index, choose):
    """
    构建决策树
    :param fa:
    :param index:
    :param treeIndex:
    :return:
    """
    if (index >= len(riskList)): return

    treeNode = TreeNode(0, 0)
    treeList.append(treeNode)

    risk = riskList[index]
    treeNode.index = len(treeList)
    treeNode.fa = fa.index if fa else -1
    riskScoreAll = fa.riskScoreAll if fa else 0
    costAll = fa.costAll if fa else 0
    treeNode.haveSon = False if (index == len(riskList) - 1) else True

    if choose == 1:
        treeNode.change(
            riskScoreAll + risk.chooseOne.riskProbability * risk.chooseOne.influenceFactor,
            costAll + risk.chooseOne.cost,
            choose
        )
    elif choose == 2:
        treeNode.change(
            riskScoreAll + risk.chooseTwo.riskProbability * risk.chooseTwo.influenceFactor,
            costAll + risk.chooseTwo.cost,
            choose
        )
    else:
        treeNode.change(
            riskScoreAll + risk.chooseThree.riskProbability * risk.chooseThree.influenceFactor,
            costAll + risk.chooseTwo.cost,
            choose
        )

    # 递归构建决策树
    treeNode.l = makeDecisionTree(treeNode, index + 1, 1)
    treeNode.m = makeDecisionTree(treeNode, index + 1, 2)
    treeNode.r = makeDecisionTree(treeNode, index + 1, 3)

    return treeNode.index


def printResult(node, index):
    """
    输出最优路径
    :param node:
    :return:
    """
    if node.fa != -1:
        printResult(treeList[node.fa - 1], index - 1)
        file.write('\n    ' + problemList[index] + ': ' + swith[node.choose - 1])


def solveOneRisk(csv_name, i):
    """
    对一个方面的风险进行求值
    :param csv_name:
    :return:
    """
    # 初始化
    global riskList, treeList, problemList, problem_num, costList
    riskList = []
    treeList = []
    problemList = []
    problem_num = -1

    preTreateData(csv_name)
    makeDecisionTree(None, 0, 1)
    makeDecisionTree(None, 0, 2)
    makeDecisionTree(None, 0, 3)

    # 结果输出
    sum = 0
    index = 0
    for each in treeList:
        if not each.haveSon:
            index += 1
            sum += each.riskScoreAll
    file.write("\n  Average risk score: " + str(sum / (1.0 * index)))

    min = 10000
    this_answer = None
    for each in treeList:
        if not each.haveSon and each.costAll <= int(costList[i - 1]) and each.riskScoreAll < min:
            min = each.riskScoreAll
            this_answer = each
    file.write("\n  Spending restrictions: " + str(costList[i - 1]))
    file.write("\n  The cost of the optimal risk strategy: " + str(this_answer.costAll))
    file.write("\n  Risk score for optimal risk strategy: " + str(this_answer.riskScoreAll))
    file.write("\n  Optimal risk strategy for the program：")
    printResult(this_answer, problem_num)


def usage():
    """
    输出帮助
    :return:
    """
    print ("\nUsage: npm <command>"
           "\n\nOptions:"
           "\n  -c    this is intake of cost params,"
           "\n        please input a string like 8,8,8,8,8,8,8,8,"
           "\n        it should include eight integer,"
           "\n        and number should not bigger than 10."
           "\n  -f    the name of output file."
           "\n  -h    help")


if __name__ == '__main__':
    # 与命令行交互
    opts, args = getopt.getopt(sys.argv[1:], "hc:f:")

    output = ""
    flag_1 = False
    flag_2 = False

    for op, value in opts:
        if op == '-c':
            costList = value.split(',')
            flag_1 = True
        elif op == '-f':
            output = value
            flag_2 = True
        elif op == '-h':
            usage()
            sys.exit()

    if flag_1 and flag_2:

        file = open(output, 'w')
        for i in range(1, 9):
            name = 'data-' + str(i) + '.csv'
            print riskName[i - 1] + 'is finished!'
            file.write('\n\n' + riskName[i - 1])
            solveOneRisk(name, i)
        file.close()
    else:
        print "Please check your input!"
