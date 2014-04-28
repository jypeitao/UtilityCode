cecho()
{
    echo -e "\033[$1m$2\033[0m"
}

getCurrentBranch()
{
    temp=`cat .git/HEAD`
    echo ${temp#ref:\ refs\/heads\/}    
}

getRecentlySubmittedID()
{
    temp=`git log -1 | grep commit`
    echo ${temp:7}
}

doPush()
{
    cecho 32 "do push to "$1" begin"
    oldBranch=`getCurrentBranch`
#    commitId=`getRecentlySubmittedID`
    commitId=$2
    sleep 1 
    git checkout $1 #xs_MP1.V2.10_CKT92_WE_KK
    git pull
    name=`date +%s` 
    git checkout -b $name
    git cherry-pick $commitId
    git push origin $name:refs/for/$1
    sleep 1
    git checkout $oldBranch
    sleep 1
    git branch -D $name
    cecho 32 "push to"$1"ok!\n"
}
if [ -z "$1" ];then
    cecho 31 "Invalid argument!"
    exit
else
    cecho 32 "commit id is: "$1
fi

cecho 32 "current branch is: "`getCurrentBranch`

doPush xs_MP1.V2.10_CKT92_WE_KK $1
sleep 5
doPush xs_MP1.V2.10_CKT92_WE_KK_XOLO $1 
